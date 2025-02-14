import operator
import warnings

from sympy import Point, Line, N


# Full Path Construction


def wild_shoot(left_primary, left_secondary, right_primary, right_secondary, t0_line, tn_line, left_channel,
               right_channel):
    left_base = Line(left_primary[2], left_secondary[2])
    left_base_t0 = t0_line.intersection(left_base)[0]
    left_base_tn = tn_line.intersection(left_base)[0]

    left_support = right_primary[2]
    distance = left_base.distance(left_support)

    # ... and its parallel
    for r in right_channel:
        # print(r[1][0])
        # limit with choke point
        temp_point = Point(*r[0])
        if left_base.distance(temp_point) < distance:
            left_support = temp_point
            distance = left_base.distance(temp_point)
    left_parallel = left_base.parallel_line(left_support)

    left_parallel_t0 = t0_line.intersection(left_parallel)[0]
    left_parallel_tn = tn_line.intersection(left_parallel)[0]

    left_path_plot = ((True, False), ((left_base_t0, left_base_tn), (left_parallel_t0, left_parallel_tn)))
    left_path = (left_base, left_support)

    right_base = Line(right_primary[2], right_secondary[2])
    right_base_t0 = t0_line.intersection(right_base)[0]
    right_base_tn = tn_line.intersection(right_base)[0]

    right_support = left_primary[2]
    distance = right_base.distance(left_primary[2])

    # ... and its parallel
    for l in left_channel:
        # limit with choke point
        temp_point = Point(*l[0])
        if right_base.distance(temp_point) < distance:
            right_support = temp_point
            distance = right_base.distance(temp_point)
    right_parallel = right_base.parallel_line(right_support)

    right_parallel_t0 = t0_line.intersection(right_parallel)[0]
    right_parallel_tn = tn_line.intersection(right_parallel)[0]

    right_path_plot = ((False, True), ((right_parallel_t0, right_parallel_tn), (right_base_t0, right_base_tn)))
    right_path = (right_base, right_support)

    return [(left_path, left_path_plot), (right_path, right_path_plot)]


def shoot(left_primary, left_secondary, right_primary, right_secondary, t0_line, tn_line):
    left_base = Line(left_primary, left_secondary)
    left_base_t0 = t0_line.intersection(left_base)[0]
    left_base_tn = tn_line.intersection(left_base)[0]

    # ... and its parallel
    # print(N(left_base.distance(right_primary)), N(left_base.distance(right_secondary)))
    if left_base.distance(right_primary) <= left_base.distance(right_secondary):
        left_support = right_primary

    else:
        left_support = right_secondary

    left_parallel = left_base.parallel_line(left_support)
    left_parallel_t0 = t0_line.intersection(left_parallel)[0]
    left_parallel_tn = tn_line.intersection(left_parallel)[0]

    left_path_plot = ((True, False), ((left_base_t0, left_base_tn), (left_parallel_t0, left_parallel_tn)))
    left_path = (left_base, left_support)

    right_base = Line(right_primary, right_secondary)
    right_base_t0 = t0_line.intersection(right_base)[0]
    right_base_tn = tn_line.intersection(right_base)[0]

    if right_base.distance(left_primary) <= right_base.distance(left_secondary):
        right_support = left_primary
    else:
        right_support = left_secondary
    right_parallel = right_base.parallel_line(right_support)
    right_parallel_t0 = t0_line.intersection(right_parallel)[0]
    right_parallel_tn = tn_line.intersection(right_parallel)[0]

    right_path_plot = ((False, True), ((right_parallel_t0, right_parallel_tn), (right_base_t0, right_base_tn)))
    right_path = (right_base, right_support)

    return [(left_path, left_path_plot), (right_path, right_path_plot)]


# Support Path Construction

def get_support(channel, base, range_f, warp_neutral, ex):
    # print("get support", channel, base, range_f, warp_neutral, ex)
    partial_channel = []
    if base.p1 == warp_neutral[2]:
        ex_degree = 0
        support = (*warp_neutral, ex_degree)
    else:
        ex_degree = base.angle_between(Line(base.p1, warp_neutral[2]))
        support = (*warp_neutral, ex_degree)
    delta = False
    for p in channel:
        if range_f(p):
            if base.p1 == p[2]:
                # print(p[1], "OUTCH!")
                partial_channel.append(p)
                continue
            # if both lines have same origin - take the angle clockwise
            partial_latitude_degree = base.angle_between(Line(base.p1, Point(p[0])))
            new_post = (*p, partial_latitude_degree)
            # print("comparing", p[1], N(partial_latitude_degree))
            partial_channel.append(new_post)

            # if ex(partial_latitude_degree, threshold) and ex(partial_latitude_degree, ex_degree):
            #    support = new_post
            # print("in range", N(partial_latitude_degree), N(ex_degree))
            if ex(partial_latitude_degree, ex_degree):
                # print("hit!", p[1], N(partial_latitude_degree), N(ex_degree))
                delta = True
                ex_degree = partial_latitude_degree
                support = new_post

    if not delta:
        warnings.warn("Watch out, bro! There is no more support ): love u tho")
    return partial_channel, support


def make_principal(channel, channel_alignment, tilt, latitude_alignment_base, choke_point):
    if channel_alignment == 'left':
        principal_warp_base = Line(Point(latitude_alignment_base[0][0]), Point(latitude_alignment_base[1][0]))
        if tilt:
            # this could be done more neatly but this is more explicit
            principal_warp_range = lambda post: post[1][1] >= choke_point[1][1]
        else:
            principal_warp_range = lambda post: post[1][1] <= choke_point[1][1]
    elif channel_alignment == 'right':
        principal_warp_base = Line(Point(latitude_alignment_base[1][0]), Point(latitude_alignment_base[0][0]))
        if tilt:
            principal_warp_range = lambda post: post[1][1] <= choke_point[1][1]
        else:
            principal_warp_range = lambda post: post[1][1] >= choke_point[1][1]
    else:
        raise ValueError("Critical Value Error, illegal channel alignment")

    # technically unnecessary, just in keeping with old conventions for the function call of get_support
    principal_warp_neutral = choke_point

    # could return these directly, also just making this more explicit
    principal_warp_channel, principal_support = get_support(channel, principal_warp_base, principal_warp_range,
                                                            principal_warp_neutral, operator.le)

    return principal_warp_channel, principal_support


def make_subordinate(ancestor, channel, channel_alignment, longitude_alignment, channel_alignment_base, warp_neutral):
    if channel_alignment == 'left':
        # this could also be simplified as an expression but being more elaborate is better here

        x_subordinate_warp_base = Line(ancestor[2], channel_alignment_base[0][2])
        ##x_subordinate_warp_base = Line(ancestor[2], channel_alignment_base[1][2])
        if longitude_alignment == 't0':
            comp = operator.le
            x_subordinate_warp_range = lambda post: post[1][0] <= warp_neutral[1][0]
        elif longitude_alignment == 'tn':
            comp = operator.ge
            x_subordinate_warp_range = lambda post: post[1][0] >= warp_neutral[1][0]
        else:
            raise ValueError("Critical Value Error, illegal longitude alignment")
    elif channel_alignment == 'right':

        x_subordinate_warp_base = Line(ancestor[2], channel_alignment_base[1][2])
        ##x_subordinate_warp_base = Line(ancestor[2], channel_alignment_base[0][2])
        if longitude_alignment == 't0':
            # operators equal
            comp = operator.le
            x_subordinate_warp_range = lambda post: post[1][0] <= warp_neutral[1][0]
        elif longitude_alignment == 'tn':
            # operators equal
            comp = operator.ge
            x_subordinate_warp_range = lambda post: post[1][0] >= warp_neutral[1][0]
        else:
            raise ValueError("Critical Value Error, illegal longitude alignment")
    else:
        raise ValueError("Critical Value Error, illegal channel alignment")

    x_subordinate_warp_channel, x_subordinate_support = get_support(channel, x_subordinate_warp_base,
                                                                    x_subordinate_warp_range, warp_neutral, comp)

    return x_subordinate_warp_channel, x_subordinate_support


# Sympy Translation

def pointify(point):
    return *point, Point(point[0])


# (full) Isocline Path Construction

def isocline_paths(choke_left, choke_right, t0, tn):
    # we shoot from the shorter to the longer goal
    # numpy allows us to do many handy things exactly,
    # we transform both supports into vectors, we discard longitude and latitude readings since we'll reconstruct them
    # exactly when we need them
    left_support = Point(choke_left[0])
    right_support = Point(choke_right[0])
    t0_line = Line(Point(t0[0]), Point(t0[1]))
    tn_line = Line(Point(tn[0]), Point(tn[1]))
    ll_line = Line(Point(t0[0]), Point(tn[0]))
    rr_line = Line(Point(t0[1]), Point(tn[1]))

    origin = ll_line.intersection(rr_line)[0]

    # there are two possible paths, one along each choke point

    # the shot path along the isocline of the left support...
    left_isocline_base = Line(left_support, origin)
    left_iso_t0l = t0_line.intersection(left_isocline_base)[0]
    left_iso_tnl = tn_line.intersection(left_isocline_base)[0]
    # ... and its parallel
    left_isocline_parallel = left_isocline_base.parallel_line(Point(right_support))
    left_iso_t0r = t0_line.intersection(left_isocline_parallel)[0]
    left_iso_tnr = tn_line.intersection(left_isocline_parallel)[0]
    # The boolean pair denotes if the sides have been constructed via points on the same side
    left_path_plot = ((True, False), ((left_iso_t0l, left_iso_tnl), (left_iso_t0r, left_iso_tnr)))
    left_path = (left_isocline_base, Point(right_support))
    # left_path_distance = left_isocline_base.distance(right_support)

    # the shot path along the isocline of the right support...
    right_isocline_base = Line(right_support, origin)
    right_iso_t0l = t0_line.intersection(right_isocline_base)[0]
    right_iso_tnl = tn_line.intersection(right_isocline_base)[0]
    # ... and its parallel
    right_isocline_parallel = right_isocline_base.parallel_line(Point(left_support))
    right_iso_t0r = t0_line.intersection(right_isocline_parallel)[0]
    right_iso_tnr = tn_line.intersection(right_isocline_parallel)[0]
    right_path_plot = ((False, True), ((right_iso_t0r, right_iso_tnr), (right_iso_t0l, right_iso_tnl)))
    right_path = (right_isocline_base, Point(left_support))
    # right_path_distance = right_isocline_base.distance(left_support)

    return [(left_path, left_path_plot), (right_path, right_path_plot)]


# Path Evaluation

def test_path(path, goal_segments, ball_radius):
    goal_validity = test_path_goals(path, goal_segments)
    goal_message = f"successful goal crossings: {len(goal_validity[1][0])}, goal violations: {len(goal_validity[1][1])} -> {"accepted" if goal_validity[0] else "rejected"}"

    width_validity = test_path_width(path, ball_radius * 2)
    width_message = f"ball diameter: {ball_radius * 2}, channel width: {width_validity[1][1]} -> {"accepted" if width_validity[0] else "rejected"}"

    verdict = goal_validity[0] and width_validity[0]
    verdict_message = f"{"Path Accepted!" if verdict else "Path Rejected!"}"

    message = goal_message + '\n' + width_message + '\n' + verdict_message

    return verdict, message


def test_path_width(path, diameter):
    success = None
    width = path[0].distance(path[1])
    if width >= diameter:
        success = True
    else:
        success = False
    return success, (diameter, N(width))


def test_path_goals(path, goals):
    path_base = path[0]
    path_parallel = path[0].parallel_line(path[1])
    accepted = []
    rejected = []
    success = True
    for g in goals:
        # print(g, path_base.intersection(g), path_parallel.intersection(g))
        if path_base.intersection(g) and path_parallel.intersection(g):
            accepted.append(g)
        else:
            success = False
            rejected.append(g)
    return success, (accepted, rejected)
