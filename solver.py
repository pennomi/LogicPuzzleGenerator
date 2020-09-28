import copy

__all__ = [
    "Problem",
]

from clues import Clue


class Problem:
    def __init__(self):
        self._constraints: [Clue] = []
        self._variables = {}

    def add_variable(self, variable, domain):
        variable = str(variable)
        if variable in self._variables:
            msg = "Tried to insert duplicated variable %s" % repr(variable)
            raise ValueError(msg)
        if hasattr(domain, "__getitem__"):
            domain = Domain(domain)
        elif isinstance(domain, Domain):
            domain = copy.copy(domain)
        else:
            msg = "Domains must be instances of subclasses of the Domain class"
            raise TypeError(msg)
        if not domain:
            raise ValueError("Domain is empty")
        self._variables[variable] = domain

    def add_variables(self, variables, domain):
        for variable in variables:
            self.add_variable(variable, domain)

    def add_constraint(self, constraint, variables=None):
        if not callable(constraint):
            msg = "Constraints must be instances of subclasses of the Constraint class"
            raise ValueError(msg)
        self._constraints.append(constraint)

    def get_solutions(self):
        domains, constraints = self._get_args()
        if not domains:
            return []
        return _recursive_backtracking([], domains, constraints, {})

    def _get_args(self):
        domains = self._variables.copy()
        all_variables = domains.keys()
        constraint_list = []
        for clue in self._constraints:
            constraint = clue
            constraint_list.append(constraint)
        constraints = {}
        for variable in domains:
            constraints[variable] = []
        for constraint in constraint_list:
            for variable in constraint.variable_names:
                constraints[variable].append(constraint)
        for constraint in constraint_list[:]:
            constraint.preprocess(constraint.variable_names, domains, constraints)
        for domain in domains.values():
            domain.reset_state()
        return domains, constraints


def _recursive_backtracking(solutions, domains, constraints, assignments):
    # Mix the Degree and Minimum Remaining Values (MRV) heuristics
    lst = [(-len(constraints[variable]), len(domains[variable]), variable) for variable in domains]
    lst.sort()
    for item in lst:
        if item[-1] not in assignments:
            # Found an unassigned variable. Let's go.
            break
    else:
        # No unassigned variables. We've got a solution.
        # print("Found a solution")
        # print(json.dumps(assignments))
        solutions.append(assignments.copy())
        return solutions

    variable = item[-1]
    assignments[variable] = None

    # Do a forward check
    push_domains = [domains[x] for x in domains if x not in assignments]

    for value in domains[variable]:
        assignments[variable] = value
        if push_domains:
            for domain in push_domains:
                domain.push_state()
        for constraint in constraints[variable]:
            if not constraint(constraint.variable_names, domains, assignments):
                # Value is not good.
                break
        else:
            # Value is good. Recurse and get next variable.
            _recursive_backtracking(solutions, domains, constraints, assignments)
        if push_domains:
            for domain in push_domains:
                domain.pop_state()
    del assignments[variable]
    return solutions


class Domain(list):
    def __init__(self, iterable):
        super().__init__(iterable)
        self._hidden = []
        self._states = []

    def reset_state(self):
        self.extend(self._hidden)
        del self._hidden[:]
        del self._states[:]

    def push_state(self):
        self._states.append(len(self))

    def pop_state(self):
        diff = self._states.pop() - len(self)
        if diff:
            self.extend(self._hidden[-diff:])
            del self._hidden[-diff:]

    def hide_value(self, value):
        list.remove(self, value)
        self._hidden.append(value)
