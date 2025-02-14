import operator

from sympy import Point, Line
from shot_path_spellbook import pointify, get_support, make_subordinate, make_principal


def construct_supports(_left_channel, _right_channel, _choke_left, _choke_right, _t0, _tn, leftwards_tilt):
    t0 = ((_t0[0], (0, 0), Point(_t0[0])), (_t0[1], (0, 1), Point(_t0[0])))
    tn = ((_tn[0], (0, 1), Point(_tn[0])), (_tn[1], (1, 1), Point(_tn[1])))

    choke_left = pointify(_choke_left)
    choke_right = pointify(_choke_right)

    left_channel = []
    right_channel = []
    for l in _left_channel:
        left_channel.append(pointify(l))
    for r in _right_channel:
        right_channel.append(pointify(r))

    # We could literally save a lot of these variables but I just need to get it done
    if leftwards_tilt:
        # print("left choke point subordinate")
        left_cp_sub_warp_channel, left_choke_point__subordinate = get_support(left_channel,
                                                                              Line(choke_left[2], t0[0][2]),
                                                                              lambda p: p[1][0] >= choke_left[1][0],
                                                                              t0[1], operator.ge)
        # print("right principal support")
        right_p_warp_channel, right_principal = get_support(right_channel, Line(t0[1][2], tn[1][2]),
                                                            lambda p: p[1][0] <= choke_right[1][0], choke_right,
                                                            operator.ge)
        # make_principal(right_channel, 'right', True, t0, choke_right)

        # print("right principal subordinate")
        right_p_sub_warp_channel, right_principal__subordinate = get_support(right_p_warp_channel,
                                                                             Line(right_principal[2], tn[1][2]),
                                                                             lambda p: p[1][0] >= right_principal[1][0],
                                                                             choke_right, operator.ge)
        # make_subordinate(right_principal, right_p_warp_channel, 'right', 't0', (t0[1], tn[1]), choke_right)

        return (choke_left, left_choke_point__subordinate), (right_principal, right_principal__subordinate)

    else:
        # print("right choke point subordinate")
        right_cp_sub_warp_channel, right_choke_point__subordinate = make_subordinate(choke_right, right_channel,
                                                                                     'right', 't0', (t0[1], tn[1]),
                                                                                     tn[1])

        # print("left principal support")
        left_p_warp_channel, left_principal = make_principal(left_channel, 'left', False, t0, choke_left)

        # print("left principal subordinate")
        left_p_sub_warp_channel, left_principal__subordinate = make_subordinate(left_principal, left_p_warp_channel,
                                                                                'left', 't0', (t0[0], tn[0]),
                                                                                choke_left)

        return (left_principal, left_principal__subordinate), (choke_right, right_choke_point__subordinate)
