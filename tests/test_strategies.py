from axelrod_fortran import characteristics


def test_original_rank():
    ranks = [
        details['original_rank']
        for details in characteristics.values()
        if details['original_rank'] is not None]

    assert len(ranks) == 63

    # Test that are no duplicates in the rank values
    assert len(ranks) == len(set(ranks))

    # There were 63 strategies in the second tournament and so every integer
    # between 1 and 63 inclusive should appear in the ranks list. Those values
    # sum to 2016.
    assert sum(ranks) == 2016
