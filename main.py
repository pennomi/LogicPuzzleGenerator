import cProfile

import clues as c
from solver import Problem


class LogicPuzzle:
    def __init__(self, domains, primary_domain=None):
        self.domains = domains
        self.primary_domain = primary_domain
        self.solution = None
        self._validate_domains()

    def _validate_domains(self):
        """Make sure that all domains are valid. This checks that:
            1. All domains must be the same length
            1. No naming overlaps occur. While it could technically be fine, overlaps confuse the user.
            1. All domains must have strings, except up to one "mathy" domain with numbers
            1. If primary_domain is given, it must be a valid domain. It must be the "mathy" domain, if it exists.
        """
        # Ensure all domains are the same length.
        target_length = len(list(self.domains.values())[0])
        for values in self.domains.values():
            if len(values) != target_length:
                raise ValueError(f"Given domains do not all have the same number of items.")

        # Ensure no naming overlaps occur.
        all_values = []
        [all_values.extend([str(v) for v in _]) for _ in self.domains.values()]
        if len(all_values) != len(set(all_values)):
            raise ValueError(f"Domains have repeated items. All items must be unique.")

        # Ensure everything is strings except up to one mathy domain, which must be integers.
        mathy_domain = None
        for domain_name, values in self.domains.items():
            types = {type(v) for v in values}
            if len(types) != 1:
                raise ValueError(f"Domain `{domain_name}` does not have exactly one data type.")
            if types not in [{int}, {str}]:
                raise ValueError(f"Domain `{domain_name}` must be of type str or int.")
            if types == {int}:
                # This is a mathy domain
                if mathy_domain:
                    raise ValueError(f"There is more than one domain with numbers specified.")
                mathy_domain = domain_name

        # Assign primary domain if it doesn't already exist
        if not self.primary_domain:
            if mathy_domain:
                self.primary_domain = mathy_domain
            else:
                self.primary_domain = list(self.domains.keys())[0]

        # primary_domain must be a valid domain, and mathy if possible.
        if self.primary_domain not in list(self.domains.keys()):
            raise ValueError(f"`{self.primary_domain}` is not one of the specified domains.")

        if mathy_domain and self.primary_domain != mathy_domain:
            raise ValueError("If a domain has numbers, it must be the primary domain.")

    def solve(self, clues: [c.Clue]):
        problem = Problem()

        for domain_name, value_list in self.domains.items():
            # Add the variables
            if domain_name == self.primary_domain:
                for var in value_list:
                    problem.add_variable(var, [var])
            else:
                problem.add_variables(value_list, self.domains[self.primary_domain])

            # Also add the constraints
            all_diff = c.AllDifferent(*[str(v) for v in value_list])
            problem.add_constraint(*all_diff.get_constraint())

        for clue in clues:
            if isinstance(clue, c.Clue):
                problem.add_constraint(*clue.get_constraint())
            else:
                problem.add_constraint(*clue)

        solutions = problem.get_solutions()
        print(f"{len(solutions)} solutions found")
        self.solution = solutions[0]

    def print_solution(self):
        domains = list(self.domains.keys())
        print("=" * 21 * len(domains))
        for d in domains:
            print(f"{str(d):^20}", end="|")
        print()
        print("=" * 21 * len(domains))

        for value in self.domains[self.primary_domain]:
            for domain_name in domains:
                var_list = [str(_) for _ in self.domains[domain_name]]
                for var_name in self.solution:
                    if self.solution[var_name] == value and var_name in var_list:
                        print(f"{str(var_name):^20}", end="|")
            print()
        print("=" * 21 * len(domains))


def main():
    puzzle = LogicPuzzle({
        "Grandchild": ["Bryan", "Franklin", "Hilda", "Kerry", "Patti", "Sadie", "Vicki"],
        "Age": ["5", "6", "8", "9", "12", "14", "18"],
        "Town": ["Cornville", "El Monte", "Fillmore", "Goldfield", "Le Mars", "Quimby", "Urbana"],
        "Birthday": [3, 7, 11, 15, 19, 23, 27],
    })

    with cProfile.Profile() as profiler:
        puzzle.solve([
            # 1. Of the child from Goldfield and the child with the April 23rd birthday, one is Franklin and the other is 8 years old.
            c.ConnectedPairs(["Goldfield", "23"], ["Franklin", "8"]),

            # 2. The 18-year-old has a birthday 4 days before Franklin.
            c.AddNEquals("18", 4, "Franklin"),

            # 3. The child from Cornville has a birthday 8 days before Sadie.
            c.AddNEquals("Cornville", 8, "Sadie"),

            # 4. The child from Le Mars has a birthday 20 days before the grandchild from Fillmore.
            c.AddNEquals("Le Mars", 20, "Fillmore"),

            # 5. The 5-year-old has a birthday 20 days after the child from Le Mars.
            c.AddNEquals("5", -20, "Le Mars"),

            # 6. The 12-year-old is either Sadie or the grandchild with the April 7th birthday.
            c.IsOneOf("12", ["Sadie", "7"]),

            # 7. The 12-year-old has a birthday sometime after Kerry.
            c.LessThan("Kerry", "12"),

            # 8. The one from Quimby isn't 14 years old.
            c.AllDifferent("Quimby", "14"),

            # 9. The child from Goldfield has a birthday 8 days before Hilda.
            c.AddNEquals("Goldfield", 8, "Hilda"),

            # 10. The one from Goldfield has a birthday 16 days before Patti.
            c.AddNEquals("Goldfield", 16, "Patti"),

            # 11. The 18-year-old has a birthday 4 days before the one from Quimby.
            c.AddNEquals("18", 4, "Quimby"),

            # 12. The 6-year-old has a birthday sometime before the 18-year-old.
            c.LessThan("6", "18"),

            # 13. The child from Cornville has a birthday sometime after Kerry.
            c.LessThan("Kerry", "Cornville"),

            # 14. The one from Urbana has a birthday 8 days after Vicki.
            c.AddNEquals("Urbana", -8, "Vicki"),

            # 15. Hilda isn't 14 years old.
            c.AllDifferent("Hilda", "14"),
        ])
    profiler.print_stats("time")

    puzzle.print_solution()


if __name__ == "__main__":
    main()

