from math import degrees, atan2
from utility import test_orientation


def read_goals(file_path):
    # this function takes the file path as input and outputs the data of the task:
    # number of goals, ball radius, list of the goals

    # open the file
    with open(file_path, "r") as file:
        # read the data
        num_goals, ball_radius = file.readline().strip().split()

        list_goals = []
        for line in file:
            coords_goal = tuple(int(num) for num in line.strip().split(" "))
            coords_posts = ((coords_goal[0], coords_goal[1]), (coords_goal[2], coords_goal[3]))
            list_goals.append(coords_posts)
    return int(num_goals), float(ball_radius), list_goals


def calculate_angle(a, x, b, clockwise):
    # this function calculates the angle at the point x
    # the parameter clockwise is a boolean:
    # depending on its value the function calculates the angle clockwise or counterclockwise

    # extract the coordinates as points
    x1, y1 = a
    x2, y2 = x
    x3, y3 = b

    # calculate the angle at point x
    deg1 = (360 + degrees(atan2(x1 - x2, y1 - y2))) % 360
    deg2 = (360 + degrees(atan2(x3 - x2, y3 - y2))) % 360

    if clockwise:
        # calculate the angle clockwise
        angle = deg2 - deg1 if deg1 <= deg2 else 360 - (deg1 - deg2)
    else:
        # calculate the angle counterclockwise
        angle = deg1 - deg2 if deg1 >= deg2 else 360 - (deg2 - deg1)

    return angle


def angle_test(list_goals):
    # Mögliche Orientierungen des ersten Tores
    possible_first_goal_configurations = [list_goals[0], (list_goals[0][1], list_goals[0][0])]

    # Es werden beide möglichen Orientierungen des ersten Tors durchgegangen, um die richtige zu finden
    for first_goal_configuration in possible_first_goal_configurations:
        # nach einer Lösung suchen
        correct_orientations = search_solution(first_goal_configuration, list_goals)

        # wenn eine Lösung gefunden wurde, kann abgebrochen werden
        if correct_orientations is not None:
            return correct_orientations

    # wenn keine Lösung gefunden wurde
    return None


def search_solution(first_goal_config, list_goals):

    # Liste mit gefunden lr-Konfigurationen
    correct_orientations = []

    # die möglichen Orientierungen des vorherigen Tores
    # das vorherige Tor wird mit dem ersten Tor initialisiert
    previous_goal_orientations = [first_goal_config]

    # Orientierungen des neuen Tors
    new_goal_orientations = []

    # mögliche Tore zwischen den previous und new goal (Beispielaufgabe 1 Tor 4)
    middle_goals = []

    # für jedes neue Tor wird die lr-Konfiguration berechnet
    for new_goal in list_goals[1:]:
        # Wenn das vorherige Tor nur eine mögliche Orientierung besitzt
        if len(previous_goal_orientations) == 1:
            # mögliche Orientierungen mit dem Orientierungstest herausfinden
            orientations = test_orientation(previous_goal_orientations[0], new_goal)
            # put it into a list of correctly oriented goals
            new_goal_orientations = [orientation[2:4] for orientation in orientations]
        else:
            # wenn es eine bifurcation gibt (also mit zwei möglichen Orientierungen des previous goals),
            new_goal_orientations = [new_goal, [new_goal[1], new_goal[0]]]

        # Die Orientierungen des previous und new goal herausfinden
        new_orientations, previous_orientations = get_new_orientations(new_goal_orientations, previous_goal_orientations)

        # Wenn es keine vorherigen oder keine neuen Orientierungen gibt
        if not new_orientations or not previous_orientations:
            return None

        # Wenn es nur eine mögliche Orientierung gibt, dann kann sie zu den richtigen Orientierungen hinzugefügt werden
        if len(previous_orientations) == 1:
            for element in previous_orientations:
                correct_orientations.append(element)

            # jedes Middle Goal muss hinzugefügt werden
            for goal in middle_goals:
                correct_orientations.append(goal)

            # Middle goals initialisieren
            middle_goals = []

            previous_goal_orientations = new_orientations
        else:
            # Middle Goal
            # Orientierungen des neuen Tors zu dem ersten Tor bekommen
            orientations = test_orientation(first_goal_config, new_goal)
            new_goal_orientations = [orientation[2:4] for orientation in orientations]

            middle_goals.append(new_goal_orientations[0])

        # das neue Tor das letzte ist und es noch zwei mögliche Orientierungen gibt
        if len(previous_goal_orientations) == 2 and new_goal == list_goals[-1]:
            # Orientierungen bekommen zu dem ersten Tor
            orientations = test_orientation(first_goal_config, previous_goal_orientations[0])
            previous_correct_orientations = [orientation[2:4] for orientation in orientations]

            # richtige Orientierung hinzufügen
            correct_orientations.append(previous_correct_orientations[0])

            # middle goals hinzufügen
            for goal in middle_goals:
                correct_orientations.append(goal)

        elif new_goal == list_goals[-1]:
            correct_orientations.append(previous_orientations[0])

    return correct_orientations


def get_new_orientations(new_goal_orientations, previous_goal_orientations):
    # mögliche Orientierungen initialisieren
    previous_working_orientations = []
    new_working_orientations = []

    # jede mögliche Orientierung durchgehen
    for previous_orientation in previous_goal_orientations:

        for new_orientation in new_goal_orientations:
            # den Winkel für den linken Pfosten berechnen im Uhrzeigersinn
            cl = new_orientation[0]
            bl = previous_orientation[0]
            al = previous_orientation[1]
            angle_l = calculate_angle(cl, bl, al, clockwise=True)

            # den Winkelt für den rechten Pfosten berechnen gegen den Uhrzeigersinn
            cr = new_orientation[1]
            br = previous_orientation[1]
            ar = previous_orientation[0]
            angle_r = calculate_angle(cr, br, ar, clockwise=False)

            # Wenn beide Winkel größer als 180° sind, kann diese Konfiguration nicht möglich sein
            if angle_l > 180 and angle_r > 180:
                continue

            # Wenn diese Orientierungen noch nicht in den Lösungen enthalten ist, kann sie hinzugefügt werden
            if previous_orientation not in previous_working_orientations:
                previous_working_orientations.append(previous_orientation)

            if new_orientation not in new_working_orientations:
                new_working_orientations.append(new_orientation)

    return new_working_orientations, previous_working_orientations
