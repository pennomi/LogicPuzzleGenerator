from clues import Clue


__all__ = [
    "Problem",
]


class Problem:
    def __init__(self):
        self._clues: [Clue] = []
        self._variables = {}

    def add_variable(self, variable, domain):
        self._variables[str(variable)] = Domain(domain)

    def add_clue(self, clue: Clue):
        self._clues.append(clue)

    def get_solutions(self):
        domains, clues = self._get_args()
        if not domains:
            return []
        return _recursive_backtracking([], domains, clues, {})

    def _get_args(self):
        domains = self._variables.copy()
        clue_list = []
        for clue in self._clues:
            clue_list.append(clue)
        clue_dict = {}
        for variable in domains:
            clue_dict[variable] = []
        for clue in clue_list:
            for variable in clue.variable_names:
                clue_dict[variable].append(clue)
        return domains, clue_dict


def _recursive_backtracking(solutions, domains, clues, assignments):
    # Prioritize these for optimal solve time
    lst = sorted((-len(clues[variable]), len(domains[variable]), variable) for variable in domains)
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

    push_domains = [domain_values for domain_name, domain_values in domains.items() if domain_name not in assignments]
    # Try every possible combination for this variable
    for value in domains[variable]:
        assignments[variable] = value
        for domain in push_domains:
            domain.push_state()
        for clue in clues[variable]:
            if not clue(domains, assignments):
                # Value is not good.
                break
        else:
            # Value is good. Move on to next variable recursively.
            _recursive_backtracking(solutions, domains, clues, assignments)
        for domain in push_domains:
            domain.pop_state()
    # We're done with this variable, unset it
    del assignments[variable]
    return solutions


class Domain(list):
    def __init__(self, iterable):
        super().__init__(iterable)
        self._hidden = []
        self._states = []

    def push_state(self):
        self._states.append(len(self))

    def pop_state(self):
        diff = self._states.pop() - len(self)
        if diff:
            self.extend(self._hidden[-diff:])
            del self._hidden[-diff:]

    def hide_value(self, value):
        self.remove(value)
        self._hidden.append(value)
