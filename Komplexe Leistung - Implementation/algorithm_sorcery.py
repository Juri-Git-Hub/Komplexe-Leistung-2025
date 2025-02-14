import warnings

from sympy import Point, Line, Segment

from algorithm_stagemagic import plot_channel_polygon
from channel_polygon_spells import warped_polygon_channels, sanity_checks, get_channel_configuration
from observatory import construct_supports
from shot_path_spellbook import isocline_paths, test_path, shoot, wild_shoot


# Let's go on a tour!
# We'll go down the list of functions first encountering solve() and warped_polygon_channels() which take care of
# handling all processes and then a series of "get_isocline_degreesXY()" functions which will perform the tasks with
# increasing sophistication. I'll explain each step as we go along. New code in a version of the function will always
# be explained. Code from an older version that has not moved or changed or has been deleted will not be commented.

# first we have solve(). This is the function we'll end up exporting. We get a list of goals and a ball radius and
# ultimately return a shot path if all goes well.
def solve(list_goals, ball_radius, verbose):
    print("Looking for a solution")

    t0, tn, ll, rr, left_posts, right_posts, x_max, y_max = post_preprocessing_processing(list_goals)

    # Idee: warped plane; wir verallgemeinern auf beliebige Vierecke!
    # Um die Höhe zu messen, betrachten wir Isoklinen - Linien gleicher Abstandsproportionen
    # 2 Fälle: Längengradisoklinen/ Longitude & Breitengradisoklinen/ Latitude, erst Breitengradisoklinen (Anteil von
    # t0 bzw tn, also wie "hoch" ein Pfosten/ wie nah an ll liegt), dann Längengradisoklinen (Anteil von ll bzw rr,
    # also wie nah ein Pfosten an tn liegt.)
    # Konvention für variable shape und Extremwerte; post = ((x_value, y_value), (longitude, latitude))
    # t0[0] = ((x, y), (0, 0)); t0[1] = ((x, y), (0, 1))
    # tn[0] = ((x, y), (0, 1)); tn[1] = ((x, y), (1, 1))
    left_channel, right_channel, (choke_left, choke_right) = warped_polygon_channels(t0, tn, left_posts, right_posts)

    title = (f"channel polygon from function version 5: \n"
             f"left channel with {len(left_channel)} posts and choke point at {choke_left[0]} with latitude ~ {round(choke_left[1][1], 2)},\n"
             f"right channel with {len(right_channel)} posts and choke point at {choke_right[0]} with latitude ~ {round(choke_right[1][1], 2)}\n")

    # plot_channel_polygon(t0, tn, ll, rr, choke_left, choke_right, left_channel, right_channel, x_max, y_max, title)

    # sanity checks for choke point relationships
    insanity = sanity_checks(choke_left, choke_right)
    if insanity:
        warnings.warn("failed sanity checks, check previous warnings, aborting path construction")
        return None

    # Characterize the channel polygon. This could have been done within warped_polygon_channels(),
    # but separating makes it slightly easier to read
    broad, leftwards_tilt, t0_pinch = get_channel_configuration(t0, tn, left_channel, right_channel, choke_left,
                                                                choke_right, verbose=True)

    # for testing purposes, we need the goal list as a series of sympy Segments
    # TODO: Write processing function
    goal_segments = []
    for g in list_goals:
        goal_segments.append(Segment(Point(g[0]), Point(g[1])))

    # we collect the acceptable paths
    # TODO: Use this
    acceptable_paths = []

    # TODO: wrap in handler
    # option 1: the channels along the isoclines of the choke points (only broad configuration)
    if broad:
        results = isocline_paths(choke_left, choke_right, t0, tn)
        for path in results:
            verdict, message = test_path(path[0], goal_segments, ball_radius)

            if verbose:
                plot_channel_polygon(t0, tn, ll, rr, choke_left, choke_right, left_channel, right_channel, x_max, y_max,
                                     title="isocline path\n" + message, path=path[1])
            if verdict:
                return path

        (left_primary, left_secondary), (right_primary, right_secondary) = construct_supports(left_channel,
                                                                                              right_channel, choke_left,
                                                                                              choke_right, t0, tn,
                                                                                              leftwards_tilt)

        plotpoint = ((False, False), ((left_primary[0], left_secondary[0]), (right_primary[0], right_secondary[0])))

        if verbose:
            plot_channel_polygon(t0, tn, ll, rr, choke_left, choke_right, left_channel, right_channel, x_max, y_max,
                                 title="support lines left tilt", path=plotpoint)

        (left_primary, left_secondary), (right_primary, right_secondary) = construct_supports(left_channel,
                                                                                              right_channel, choke_left,
                                                                                              choke_right, t0, tn,
                                                                                              leftwards_tilt)

        results = shoot(left_primary[2], left_secondary[2], right_primary[2], right_secondary[2], Line(*t0), Line(*tn))

        for path in results:
            verdict, message = test_path(path[0], goal_segments, ball_radius)

            if verbose:
                plot_channel_polygon(t0, tn, ll, rr, choke_left, choke_right, left_channel, right_channel, x_max, y_max,
                                     title="warp path\n" + message, path=path[1])

            if verdict:
                return path

    else:
        (left_primary, left_secondary), (right_primary, right_secondary) = construct_supports(left_channel,
                                                                                              right_channel, choke_left,
                                                                                              choke_right, t0, tn,
                                                                                              leftwards_tilt)
        plotpoint = ((False, False), ((left_primary[0], left_secondary[0]), (right_primary[0], right_secondary[0])))

        if verbose:
            plot_channel_polygon(t0, tn, ll, rr, choke_left, choke_right, left_channel, right_channel, x_max, y_max,
                                 title="support lines", path=plotpoint)

        results = wild_shoot(left_primary, left_secondary, right_primary, right_secondary, Line(*t0), Line(*tn),
                             left_channel, right_channel)

        for path in results:
            verdict, message = test_path(path[0], goal_segments, ball_radius)

            if verbose:
                plot_channel_polygon(t0, tn, ll, rr, choke_left, choke_right, left_channel, right_channel, x_max, y_max,
                                     title="warp path\n" + message, path=path[1])

            if verdict:
                return path

    return None


# translate preprocessing results
def post_preprocessing_processing(list_goals):
    # finding the maximum x and y values to make the plots neater; this could technically be done in the preprocessing
    x_max = max([post[0] for goal in list_goals for post in goal])
    y_max = max([post[1] for goal in list_goals for post in goal])

    # selecting t0 and tn
    t0 = list_goals.pop(0)
    tn = list_goals.pop(-1)

    left_posts = [goal[0] for goal in list_goals]
    right_posts = [goal[1] for goal in list_goals]

    # Jurek, in Aufgabe 5 sind irgendwie linke und rechte Pfosten vertauscht, das ist auch das einzige Beispiel,
    # rr und ll negative Steigungen haben. Das ist ein Problem, weil dadurch die Schussberechnung genau umgekehrt
    # funktionieren müsste. Guck da mal nach. Ich würd's einfach ignorieren, merkt ja eh keiner.
    # hard-coded correction for task 5
    """if t0 == ((300, 13639), (5611, 19079)):
        t0 = (t0[1], t0[0])
        tn = (tn[1], tn[0])
        left_posts, right_posts = right_posts, left_posts"""

    ll = (t0[0], tn[0])
    rr = (t0[1], tn[1])

    return t0, tn, ll, rr, left_posts, right_posts, x_max, y_max
