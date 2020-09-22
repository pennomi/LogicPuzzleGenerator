import json
import copy

__all__ = [
    "Problem",
]


class Problem:
    def __init__(self):
        self._solver = RecursiveBacktrackingSolver()
        self._constraints = []
        self._variables = {}

    def add_variable(self, variable, domain):
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
        self._constraints.append((Constraint(constraint), variables))

    def get_solutions(self):
        domains, constraints = self._get_args()
        if not domains:
            return []
        return self._solver.get_solutions(domains, constraints)

    def _get_args(self):
        domains = self._variables.copy()
        all_variables = domains.keys()
        constraint_list = []
        for constraint, variables in self._constraints:
            if not variables:
                variables = list(all_variables)
            constraint_list.append((constraint, variables))
        constraints = {}
        for variable in domains:
            constraints[variable] = []
        for constraint, variables in constraint_list:
            for variable in variables:
                constraints[variable].append((constraint, variables))
        for constraint, variables in constraint_list[:]:
            constraint.preprocess(variables, domains, constraints)
        for domain in domains.values():
            domain.reset_state()
        return domains, constraints


class RecursiveBacktrackingSolver:
    def recursive_backtracking(self, solutions, domains, constraints, assignments):
        # Mix the Degree and Minimum Remaining Values (MRV) heuristics
        lst = [(-len(constraints[variable]), len(domains[variable]), variable) for variable in domains]
        lst.sort()
        for item in lst:
            if item[-1] not in assignments:
                # Found an unassigned variable. Let's go.
                break
        else:
            # No unassigned variables. We've got a solution.
            print("Found a solution")
            print(json.dumps(assignments))
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
            for constraint, variables in constraints[variable]:
                if not constraint(variables, domains, assignments):
                    # Value is not good.
                    break
            else:
                # Value is good. Recurse and get next variable.
                self.recursive_backtracking(solutions, domains, constraints, assignments)
            if push_domains:
                for domain in push_domains:
                    domain.pop_state()
        del assignments[variable]
        return solutions

    def get_solutions(self, domains, constraints):
        return self.recursive_backtracking([], domains, constraints, {})


Unassigned = "Unassigned"


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


class Constraint:
    def __init__(self, func):
        self._func = func

    def __call__(
        self,
        variables,
        domains,
        assignments,
    ):
        parameters = [assignments.get(x, Unassigned) for x in variables]
        if Unassigned in parameters:
            return self.forward_check(variables, domains, assignments)
        return self._func(*parameters)

    def preprocess(self, variables, domains, constraints):
        """
        Preprocess variable domains

        This method is called before starting to look for solutions,
        and is used to prune domains with specific constraint logic
        when possible. For instance, any constraints with a single
        variable may be applied on all possible values and removed,
        since they may act on individual values even without further
        knowledge about other assignments.

        @param variables: Variables affected by that constraint, in the
                          same order provided by the user
        @type  variables: sequence
        @param domains: Dictionary mapping variables to their domains
        @type  domains: dict
        @param constraints: Dictionary mapping variables to a list of
                             constraints affecting the given variables.
        @type  constraints: dict
        """
        if len(variables) == 1:
            variable = variables[0]
            domain = domains[variable]
            for value in domain[:]:
                if not self(variables, domains, {variable: value}):
                    domain.remove(value)
            constraints[variable].remove((self, variables))

    def forward_check(self, variables, domains, assignments):
        """
        Helper method for generic forward checking

        Currently, this method acts only when there's a single
        unassigned variable.

        @param variables: Variables affected by that constraint, in the
                          same order provided by the user
        @type  variables: sequence
        @param domains: Dictionary mapping variables to their domains
        @type  domains: dict
        @param assignments: Dictionary mapping assigned variables to their
                            current assumed value
        @type  assignments: dict
        @return: Boolean value stating if this constraint is currently
                 broken or not
        @rtype: bool
        """
        unassigned_variable = Unassigned
        for variable in variables:
            if variable not in assignments:
                if unassigned_variable is Unassigned:
                    unassigned_variable = variable
                else:
                    break
        else:
            if unassigned_variable is not Unassigned:
                # Remove from the unassigned variable domain's all
                # values which break our variable's constraints.
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
