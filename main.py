import cProfile
import pstats

import clues
from solver import Problem


DOMAINS = {
    "Runner": ["Anthony", "Herman", "Isaac", "Jay", "Kelly", "Lynn", "Matthew"],
    "Shirt": ["Black", "Gray", "Indigo", "Orange", "Red", "White", "Yellow"],
    "Town": ["Bellflower", "Corinth", "Fullerton", "Janesville", "Norway", "Waldoboro", "Zamora"],
    "Time": ["21", "22", "23", "24", "25", "26", "27"],
}


def main():
    problem = Problem()

    criteria = []
    for _ in DOMAINS.values():
        criteria.extend(_)

    problem.add_variables(criteria, [21, 22, 23, 24, 25, 26, 27])

    for _ in DOMAINS.values():
        problem.add_constraint(clues.all_different(), _)

    clue_list = [
        # Bind the time variables
        (lambda a: a == 21, ["21"]),
        (lambda a: a == 22, ["22"]),
        (lambda a: a == 23, ["23"]),
        (lambda a: a == 24, ["24"]),
        (lambda a: a == 25, ["25"]),
        (lambda a: a == 26, ["26"]),
        (lambda a: a == 27, ["27"]),

        # 1. The runner from Waldoboro, the runner who finished in 26 minutes, Kelly, the competitor in the white shirt and the runner in the indigo shirt were all different runners.
        (clues.all_different(), ["Waldoboro", "26", "Kelly", "White", "Indigo"]),

        # 2. Anthony finished 1 minute after the competitor from Norway.
        (clues.add_n_equals(1), ["Norway", "Anthony"]),

        # 3. The competitor from Zamora was either Herman or the competitor who finished in 25 minutes.
        (clues.is_one_of(), ["Zamora", "Herman", "25"]),

        # 4. Herman finished sometime before the contestant in the indigo shirt.
        (clues.greater_than(), ["Indigo", "Herman"]),

        # 5. The competitor from Fullerton was either the contestant who finished in 23 minutes or the competitor who finished in 25 minutes.
        (clues.is_one_of(), ["Fullerton", "23", "25"]),

        # 6. Of the runner who finished in 21 minutes and the runner from Fullerton, one was Isaac and the other wore the black shirt.
        (clues.connected_pairs(), ["21", "Fullerton", "Isaac", "Black"]),

        # 7. Jay finished 5 minutes after the competitor from Corinth.
        (clues.add_n_equals(5), ["Corinth", "Jay"]),

        # 8. Herman was either the runner from Waldoboro or the contestant from Norway.
        (clues.is_one_of(), ["Herman", "Waldoboro", "Norway"]),

        # 9. Neither the runner who finished in 21 minutes nor Herman was the runner in the gray shirt.
        (clues.all_different(), ["21", "Herman", "Gray"]),

        # 10. The competitor from Bellflower didn't wear the gray shirt.
        (clues.all_different(), ["Bellflower", "Gray"]),

        # 11. The contestant from Norway finished sometime after the runner in the red shirt.
        (clues.greater_than(), ["Norway", "Red"]),

        # 12. Jay finished sometime before the competitor in the orange shirt.
        (clues.greater_than(), ["Orange", "Jay"]),

        # 13. The contestant from Fullerton finished sometime before the runner from Waldoboro.
        (clues.greater_than(), ["Waldoboro", "Fullerton"]),

        # 14. Of the competitor from Norway and the competitor who finished in 21 minutes, one wore the red shirt and the other was Lynn.
        (clues.connected_pairs(), ["Norway", "21", "Red", "Lynn"])
    ]

    for clue in clue_list:
        problem.add_constraint(*clue)

    with cProfile.Profile() as profiler:
        solution = problem.get_solutions()[0]
    profiler.print_stats(pstats.SortKey.TIME)

    for i in [21, 22, 23, 24, 25, 26, 27]:
        for x in solution:
            if solution[x] == i:
                print(str(i), x)


if __name__ == "__main__":
    main()

