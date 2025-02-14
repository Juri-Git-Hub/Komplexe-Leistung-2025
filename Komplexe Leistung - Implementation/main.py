from preprocess import read_goals, angle_test
from algorithm_sorcery import solve
from utility import calculate_shot_path
from algorithm_stagemagic import plotSolution
from termcolor import colored


def main(task, verbose):

    task = task.strip()
    if task == "all":
        exercises = range(1, 6)
    else:
        exercises = [int(task)]

    # für jede ausgewählte Beispielaufgabe das Programm durchführen
    for ex in exercises:
        print(f"Working on exercise {ex}")

        # Tore einlesen
        num_goals, ball_radius, list_goals = read_goals(f"./tests/krocket{ex}.txt")

        # Winkeltest durchführen
        oriented_list_goals = angle_test(list_goals)

        # Wenn der Winkeltest keine Tore zurückgibt, gibt es keine Lösung
        if not oriented_list_goals:
            print(f"The Linear Ordering Test found misaligned goals. ")
            print(colored(f"There doesn't exist a solution for exercise {ex}!", "red"))
            print("\n")
            continue

        print(f"Successfully identified orientation of goals for exercise {ex}")

        # Löse die Aufgabe mithilfe der richtig orientierten Tore und dem Ballradius
        solution = solve(oriented_list_goals, ball_radius, verbose)

        if solution:
            # Den Startpunkt und die Richtung für die Lösung berechnen
            solution = calculate_shot_path(solution[1][1])

            if verbose:
                plotSolution(list_goals, [((solution.p1.x.evalf(), solution.p1.y.evalf()), (solution.p2.x.evalf(), solution.p2.y.evalf()))])

            print(colored(f"There exists a solution for exercise {ex}:", "green"))
            print(f"The startpoint is: ({solution.p1.x.evalf()}, {solution.p1.y.evalf()})")
            print(f"And the direction is: ({solution.p2.x.evalf()}, {solution.p2.y.evalf()})")
        else:
            print(colored(f"There doesn't exist a solution for exercise {ex}", "red"))

        print("\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="Task Krocket 43. BWINF",
        description="By Jurek Engelmann"
    )

    parser.add_argument(
        "-i",
        "--input",
        default="all",
        help="Choose the example task by it's number or enter all"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action='store_true',
        help="Verbose"
    )
    args = parser.parse_args()

    if args.input not in ["all", "1", "2", "3", "4", "5"]:
        raise ValueError("Invalid Input! Please choose one of the following: 1, 2, 3, 4, 5, all")

    main(args.input, args.verbose)

