from axelrod_fortran import characteristics


def test_original_rank():
    ranks = [
        details['original_rank']
        for details in characteristics.values()
        if details['original_rank'] is not None]

    assert sorted(ranks) == list(range(1, 63 + 1))
