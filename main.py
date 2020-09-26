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
PRIMARY_DOMAIN = "Birthday"  # Primary domain should be the mathy domain if one exists


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

