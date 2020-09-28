"""Clue classes for the puzzle."""


Unassigned = "Unassigned"


def _unique(iterable):
    return len(set(iterable)) == len(iterable)


class Clue:
    def __init__(self, variable_names):
        self.variable_names = variable_names

    def execute(self, *values):
        raise NotImplementedError()

    def __call__(
        self,
        variables,
        domains,
        assignments,
    ):
        parameters = [assignments.get(x, Unassigned) for x in variables]
        if Unassigned in parameters:
            return self.forward_check(variables, domains, assignments)
        return self.execute(*parameters)

    def preprocess(self, variables, domains, constraints):
        if len(variables) == 1:
            variable = variables[0]
            domain = domains[variable]
            for value in domain[:]:
                if not self(variables, domains, {variable: value}):
                    domain.remove(value)
            constraints[variable].remove((self, variables))

    def forward_check(self, variables, domains, assignments):
        unassigned_variable = Unassigned
        for variable in variables:
            if variable not in assignments:
                if unassigned_variable is Unassigned:
                    unassigned_variable = variable
                else:
                    break
        else:
            if unassigned_variable is not Unassigned:
                domain = domains[unassigned_variable]
                if domain:
                    for value in domain[:]:
                        assignments[unassigned_variable] = value
                        if not self(variables, domains, assignments):
                            domain.hide_value(value)
                    del assignments[unassigned_variable]
                if not domain:
                    return False
        return True

    def get_constraint(self):
        return self, self.variable_names


class ConnectedPairs(Clue):
    def __init__(self, list1, list2):
        if len(list1) != len(list2):
            raise ValueError("list1 and list2 must be of equal length")
        super().__init__(list1 + list2)

    def execute(self, *values):
        count = len(values)
        first_half = values[:count//2]
        second_half = values[count//2:]

        # Check that the first half lines up exactly with the second half
        return set(first_half) == set(second_half)


class AddNEquals(Clue):
    def __init__(self, smaller, integer, larger):
        self.integer = integer
        super().__init__([smaller, larger])

    def execute(self, *values):
        smaller, larger = values
        return smaller + self.integer == larger


class LessThan(Clue):
    def __init__(self, smaller, larger):
        super().__init__([smaller, larger])

    def execute(self, *values):
        smaller, larger = values
        return smaller < larger


class Equals(Clue):
    def __init__(self, left, right):
        super().__init__([left, right])

    def execute(self, *values):
        left, right = values
        return left == right


class AllDifferent(Clue):
    def __init__(self, *items):
        super().__init__(items)

    def execute(self, *items):
        return _unique(items)


class IsOneOf(Clue):
    def __init__(self, variable, items):
        super().__init__([variable, *items])

    def execute(self, first, *items):
        # Args must be unique
        # if not _unique(items):
        #     return False

        # Make sure that the first thing is included in the args
        return first in set(items)
