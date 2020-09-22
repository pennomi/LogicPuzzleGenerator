
def greater_than():
    def inside(x, y):
        return x > y
    return inside


def add_n_equals(n):
    def inside(x, y):
        return x + n == y
    return inside


def equals():
    def inside(x, y):
        return x == y
    return inside


def all_different():
    def inside(*args):
        return _unique(args)
    return inside


def _unique(iterable):
    return len(set(iterable)) == len(iterable)


def connected_pairs():
    def inside(*args):
        count = len(args)
        if count % 2:
            raise IndexError("Cannot pass an odd number of args to connected_pairs")
        first_half = args[:count//2]
        second_half = args[count//2:]

        # Check that each group is unique
        if not _unique(first_half) or not _unique(second_half):
            return False

        # Check that the first half lines up exactly with the second half
        return set(first_half) == set(second_half)

    return inside


def is_one_of():
    def inside(first, *args):
        # Args must be unique
        if not _unique(args):
            return False

        # Make sure that the first thing is included in the args
        return first in set(args)
    return inside
