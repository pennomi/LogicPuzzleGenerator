import cProfile
import pstats

import clues
from solver import Problem


DOMAINS = {
    "Grandchild": ["Bryan", "Franklin", "Hilda", "Kerry", "Patti", "Sadie", "Vicki"],
    "Age": ["5", "6", "8", "9", "12", "14", "18"],
    "Town": ["Cornville", "El Monte", "Fillmore", "Goldfield", "Le Mars", "Quimby", "Urbana"],
    "Birthday": [3, 7, 11, 15, 19, 23, 27],
}
PRIMARY_DOMAIN = "Birthday"  # Primary domain should be the mathy domain (if one exists)


class LogicPuzzle:
    def __init__(self, domains, primary_domain=None):
        self.domains = domains
        self.primary_domain = primary_domain
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
            raise ValueError(f"Given domains have repeated items.")

        # Ensure everything is strings except up to one mathy domain, which must be integers.
        mathy_domain = None
        for domain_name, values in self.domains.items():
            types = {type(v) for v in values}
            if len(types) != 1:
                raise ValueError(f"Domain `{domain_name}` does not have exactly one data type.")
            if types not in [{int}, {str}]:
                raise ValueError(f"Domain `{domain_name}` ")
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


puzzle = LogicPuzzle(DOMAINS)


def main():
    problem = Problem()

    for domain_name, value_list in DOMAINS.items():
        # Add the variables
        if domain_name == PRIMARY_DOMAIN:
            for var in value_list:
                # Ensure this is a numerical one?
                problem.add_variable(var, [var])
        else:
            problem.add_variables(value_list, DOMAINS[PRIMARY_DOMAIN])

        # Also add the constraints
        problem.add_constraint(clues.all_different(), [str(v) for v in value_list])

    clue_list = [
        # 1. Of the child from Goldfield and the child with the April 23rd birthday, one is Franklin and the other is 8 years old.
        (clues.connected_pairs(), ["Goldfield", "23", "Franklin", "8"]),

        # 2. The 18-year-old has a birthday 4 days before Franklin.
        (clues.add_n_equals(4), ["18", "Franklin"]),

        # 3. The child from Cornville has a birthday 8 days before Sadie.
        (clues.add_n_equals(8), ["Cornville", "Sadie"]),

        # 4. The child from Le Mars has a birthday 20 days before the grandchild from Fillmore.
        (clues.add_n_equals(20), ["Le Mars", "Fillmore"]),

        # 5. The 5-year-old has a birthday 20 days after the child from Le Mars.
        (clues.add_n_equals(-20), ["5", "Le Mars"]),

        # 6. The 12-year-old is either Sadie or the grandchild with the April 7th birthday.
        (clues.is_one_of(), ["12", "Sadie", "7"]),

        # 7. The 12-year-old has a birthday sometime after Kerry.
        (clues.greater_than(), ["12", "Kerry"]),

        # 8. The one from Quimby isn't 14 years old.
        (clues.all_different(), ["Quimby", "14"]),

        # 9. The child from Goldfield has a birthday 8 days before Hilda.
        (clues.add_n_equals(8), ["Goldfield", "Hilda"]),

        # 10. The one from Goldfield has a birthday 16 days before Patti.
        (clues.add_n_equals(16), ["Goldfield", "Patti"]),

        # 11. The 18-year-old has a birthday 4 days before the one from Quimby.
        (clues.add_n_equals(4), ["18", "Quimby"]),

        # 12. The 6-year-old has a birthday sometime before the 18-year-old.
        (clues.greater_than(), ["18", "6"]),

        # 13. The child from Cornville has a birthday sometime after Kerry.
        (clues.greater_than(), ["Cornville", "Kerry"]),

        # 14. The one from Urbana has a birthday 8 days after Vicki.
        (clues.add_n_equals(-8), ["Urbana", "Vicki"]),

        # 15. Hilda isn't 14 years old.
        (clues.all_different(), ["Hilda", "14"]),
    ]

    for clue in clue_list:
        problem.add_constraint(*clue)

    with cProfile.Profile() as profiler:
        solution = problem.get_solutions()[0]
    profiler.print_stats(pstats.SortKey.TIME)

    for i in DOMAINS[PRIMARY_DOMAIN]:
        for x in solution:
            if solution[x] == i:
                print(str(i), x)


if __name__ == "__main__":
    main()

