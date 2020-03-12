from collections import defaultdict
from ctypes import cdll
from ctypes.util import find_library
from multiprocessing.managers import BaseManager
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import uuid


def load_library(filename):
    """Loads a shared library."""
    lib = None
    if Path(filename).exists():
        lib = cdll.LoadLibrary(filename)
    return lib


class SharedLibraryManager(object):
    """LibraryManager creates (and deletes) copies of a shared library, which
    enables multiple copies of the same strategy to be run without the end user
    having to maintain many copies of the shared library.

    This works by making a copy of the shared library file and loading it into
    memory again. Loading the same file again will return a reference to the
    same memory addresses. To be thread-safe, this class just passes filenames
    back to the Player class (which actually loads a reference to the library),
    ensuring that multiple copies of a given player type do not use the same
    copy of the shared library.
    """

    def __init__(self, shared_library_name, verbose=False):
        self.shared_library_name = shared_library_name
        self.verbose = verbose
        self.filenames = []
        self.player_indices = defaultdict(set)
        self.player_next = defaultdict(set)
        # Generate a random prefix for tempfile generation
        self.prefix = str(uuid.uuid4())
        self.library_path = self.find_shared_library(shared_library_name)

    def find_shared_library(self, shared_library_name):
        # Hack for Linux since find_library doesn't return the full path.
        if 'Linux' in platform.system():
            output = subprocess.check_output(["ldconfig", "-p"])
            for line in str(output).split(r"\n"):
                rhs = line.split(" => ")[-1]
                if shared_library_name in rhs:
                    return rhs
            raise ValueError("{} not found".format(shared_library_name))
        else:
            return find_library(
                shared_library_name.replace("lib", "").replace(".so", ""))

    def create_library_copy(self):
        """Create a new copy of the shared library."""
        # Copy the library file to a new (temp) location.
        temp_directory = tempfile.gettempdir()
        copy_number = len(self.filenames)
        filename = "{}-{}-{}".format(
            self.prefix,
            str(copy_number),
            self.shared_library_name)
        new_filename = str(Path(temp_directory, filename))
        if self.verbose:
            print("Loading {}".format(new_filename))
        shutil.copy2(self.library_path, new_filename)
        self.filenames.append(new_filename)

    def next_player_index(self, name):
        """Determine the index of the next free shared library copy to
        allocate for the player. If none is available then make another copy."""
        # Is there a free index?
        if len(self.player_next[name]) > 0:
            return self.player_next[name].pop()
        # Do we need to load a new copy?
        player_count = len(self.player_indices[name])
        if player_count == len(self.filenames):
            self.create_library_copy()
            return player_count
        # Find the first unused index
        for i in range(len(self.filenames)):
            if i not in self.player_indices[name]:
                return i
        raise ValueError("We shouldn't be here.")

    def get_filename_for_player(self, name):
        """For a given player return a filename for a copy of the shared library
        for use in a Player class, along with an index for later releasing."""
        index = self.next_player_index(name)
        self.player_indices[name].add(index)
        if self.verbose:
            print("allocating {}".format(index))
        return index, self.filenames[index]

    def release(self, name, index):
        """Release the copy of the library so that it can be re-allocated."""
        self.player_indices[name].remove(index)
        if self.verbose:
            print("releasing {}".format(index))
        self.player_next[name].add(index)

    def __del__(self):
        """Cleanup temp files on object deletion."""
        for filename in self.filenames:
            path = Path(filename)
            if path.exists():
                if self.verbose:
                    print("deleting", str(path))
                path.unlink()


# Setup up thread safe library manager.
class MultiprocessManager(BaseManager):
    pass


MultiprocessManager.register('SharedLibraryManager', SharedLibraryManager)
