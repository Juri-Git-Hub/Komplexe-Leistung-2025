import operator
import warnings
from math import sqrt


# Channel Polygon Construction

## IMPORTANT: THIS HAS BEEN CHANGED! EVERY POST NOW HAS THE SHAPE ((x, y), (longitude, latitude))
# This function "normalizes" any quadrilateral and its associated points into a 1x1 square. We achieve this without
 # having to resort to complex algebra but only using relatively simple geometry (but a lot of it)
def warped_polygon_channels(t0, tn, left_posts, right_posts):

    # if the ll- and rr-line of the initial channel polygon (rectangle, known as the Jur-eck in the original German)
    # are not parallel to each other, they have a common origin outside the channel polygon which is also the shared
    # origin of all isoclines with rr and ll being the most extreme isoclines at 0 and 1. These are the latitude values
    # TODO: parallel goals or ll/rr lines are not part of the exercises so we ignore this edge case.
    # Analogously, we can construct the longitutde values using t0 and tn

    # treating the lines as linear functions, we can find their intersection (the "origin")
     # This means, that we construct a slope from the interval and use that to determine the intercept et voilá, we have
     # a linear function. These functions cross at some point if they are not parallel (again, not relevant for our
     # project) and we name the resulting intersection the "origin" for the latitude or longitude readings respecitvely.
     # The name comes from the idea that any initial rectangle is an intersection of 2 pairs of lines (t0 and tn as the
     # first pair and ll and rr as the second pair) and each pair originates from a single point. The huge advantage
     # this way is that if you connect any point within the channel polygon with the origin of one pair, it will cross
     # both lines of the other pair at exactly the same proportion. Try it out for yourself! This way, we can now play
     # the game as though we had a 1x1 square - we just use the latitude and longitude values that will always be
     # between 0 and 1. If a point is outside of the channel polygon, we flatly set the value to -1 if it is outside the
     # polygon but closer to t0 than tn for latitude and 2 in the other case and for longitude, we set it to -1 if it is
     # outside the channel polygon but closer to ll than to rr. See the implementations of linear intersection and get
     # anchor for details.
    ll, rr = zip(t0, tn)
    latitude_origin = linear_intersection(ll, rr)
    longitude_origin = linear_intersection(t0, tn)

    # note that the origin will always lie closer to the shorter goal. There can be arguments about which one to use but
    # it doesn't truly matter, so we'll just skip that argument for now.
    # the respective size is stored as we'll need it later
    # TODO: the size of the anchor goal is only needed as long as there can be goal posts outside of the channel
    #  polygon. We could remedy this in the preprocessing but it's not important for now.
    latitude_anchor, latitude_anchor_size = get_anchor(t0, tn)
    longitude_anchor, longitude_anchor_size = get_anchor(ll, rr)


    # We now have points with which to construct isoclines for any given point on the warped plane and anchor lines
     # to take isocline readings using "relative_line_position1()" or "relative_line_position2()", the differences
     # between them will come up soon. But for the purposes of this function, we can proceed with calculating the values
     # for all posts. You can find all utility functions at the bottom of this file.

    # The 5 different versions of get_isocline_degrees are getting better at reducing the number of invalid goals so
     # that constructing the shot path is as simple as possible with the fewest number of goals achievable in linear
     # time.

    # this loop is only here for demonstration purposes, as is the title and the plotting function. We can use them in
     # main when everything is done.
    """for f in [get_isocline_degrees1,
              get_isocline_degrees2, get_isocline_degrees3,
              get_isocline_degrees4, get_isocline_degrees5]:
        left_channel, right_channel, (choke_left, choke_right) = f(t0, tn, left_posts, right_posts,
                                                                   latitude_origin,
                                                                   latitude_anchor, latitude_anchor_size,
                                                                   longitude_origin,
                                                                   longitude_anchor, longitude_anchor_size)
        title = (f"channel polygon from function \n{f}: \n"
                 f"left channel with {len(left_channel)} posts and choke point at {choke_left[0]} with latitude ~ {round(choke_left[1][1], 2)},\n"
                 f"right channel with {len(right_channel)} posts and choke point at {choke_right[0]} with latitude ~ {round(choke_right[1][1], 2)}\n")"""
    left_channel, right_channel, (choke_left, choke_right) = get_isocline_degrees5(t0, tn, left_posts, right_posts,
                                                                   latitude_origin,
                                                                   latitude_anchor, latitude_anchor_size,
                                                                   longitude_origin,
                                                                   longitude_anchor, longitude_anchor_size)
        #plot_channel_polygon(t0, tn, ll, rr, choke_left, choke_right, left_channel, right_channel, max_x, max_y, title)
        #input("press a key to move on")

    return left_channel, right_channel, (choke_left, choke_right)


## IMPORTANT: THIS HAS BEEN CHANGED! EVERY POST NOW HAS THE SHAPE ((x, y), (longitude, latitude))
# this is my final form: determining the only relevant local extrema
def get_isocline_degrees5(t0, tn, left_posts, right_posts,
                         latitude_origin, latitude_anchor, latitude_anchor_size,
                         longitude_origin, longitude_anchor, longitude_anchor_size):
    # example: looking for the latitude maximum (choke point extremum) and local minima along the left channel
    # The average problem will have an abundance of local extrema with the latitude value constantly going up and down
     # along the channel line. Between these many minor peaks (local maxima, most of which are irrelevant) are equally
     # uninteresting local minima. Removing the local minima can drastically lower the number of remaining posts and
     # smooth the channel lines.
     # Removing the minima in the first pass will get us only a minimal computation advantage for our shot path
     # calculation as we will not reduce the number of true candidates. However, since we're doing a forwards and a
     # backwards correction, the effect will stack leading to the removal of more irrelevant posts and potentially
     # irrelevant loval maxima on the backwards correction.

    compass = ((latitude_origin, latitude_anchor, latitude_anchor_size),
               (longitude_origin, longitude_anchor, longitude_anchor_size))
    t0_0 = (t0[0], (0, 0))
    t0_1 = (t0[1], (0, 1))
    tn_0 = (tn[0], (1, 0))
    tn_1 = (tn[1], (1, 1))

    # To do this, we revise our abstract isocline degree function to include a checking mechanism before a post is
     # added to the channel and the relevant running variables keeping track of the current status. The tracking
     # variables have to be coded into the abstract function which means that there is no static 'comparator function'
     # that can just be passed to the function as we did before. A purely abstract isocline function that could be
     # modified into version 4 or even earlier versions would have to rely on powerful higher-order functions, complex
     # object-oriented inheritance or equally mighty approaches. I'll spare you from this; interesting stuff tho, haha
     # see implementation of get_isocline_degrees_abstract2() for details

    # A note:
     # It is possible to remove the valley points before doing the overhang correction. However, this would vastly limit
     # the effectiveness of the valley point removal and you wouldn't either get very far with 2 passes or, if you were
     # to implement it that way, would do so many passes that you end up with a runtime complexity of O(n log n) and we
     # can't have that.

    #print("forwards correction, left channel")
    left_fwd, choke_left_fwd = get_isocline_degrees_abstract2(initial_post=t0_0, terminal_post=tn_0, posts=left_posts,
                                                              compass=compass, isoclines_established=False,
                                                              latitude_comp=operator.ge, longitude_comp=operator.ge,
                                                              extreme_comp=operator.gt)

    #print("forwards correction, right channel")
    right_fwd, choke_right_fwd = get_isocline_degrees_abstract2(initial_post=t0_1, terminal_post=tn_1,
                                                                posts=right_posts,
                                                                compass=compass, isoclines_established=False,
                                                                latitude_comp=operator.le, longitude_comp=operator.ge,
                                                                extreme_comp=operator.lt)

    #print("backwards correction, left channel")
    left_channel, choke_left = get_isocline_degrees_abstract2(initial_post=tn_0, terminal_post=t0_0,
                                                              posts=left_fwd[::-1],
                                                              compass=compass, isoclines_established=True,
                                                              latitude_comp=operator.ge, longitude_comp=operator.le,
                                                              extreme_comp=operator.gt)

    #print("backwards correction, right channel")
    right_channel, choke_right = get_isocline_degrees_abstract2(initial_post=tn_1, terminal_post=t0_1,
                                                                posts=right_fwd[::-1],
                                                                compass=compass, isoclines_established=True,
                                                                latitude_comp=operator.le, longitude_comp=operator.le,
                                                                extreme_comp=operator.lt)

    left_channel = left_channel[::-1]
    right_channel = right_channel[::-1]

    # sanity check, only check coordinates
    if choke_left[1] != choke_left_fwd[1]:
        raise Warning(f"mismatch in identified left choke point. something went wrong, maybe equal choke points? \n"
                      f"after forwards correction: {choke_left_fwd}, after backwards correction: {choke_left}")
    if choke_right[1] != choke_right_fwd[1]:
        raise Warning(f"mismatch in identified right choke point. something went wrong, maybe equal choke points? \n"
                      f"after forwards correction: {choke_right_fwd}, after backwards correction: {choke_right}")

    return left_channel, right_channel, (choke_left, choke_right)

## IMPORTANT: THIS HAS BEEN CHANGED! EVERY POST NOW HAS THE SHAPE ((x, y), (longitude, latitude))
# a revised abstract function, ready for detecting local extrema
def get_isocline_degrees_abstract2(initial_post, terminal_post, posts,
                                   compass, isoclines_established,
                                   latitude_comp, longitude_comp, extreme_comp):

    ((latitude_origin, latitude_anchor, latitude_anchor_size),
     (longitude_origin, longitude_anchor, longitude_anchor_size)) = compass
    channel = []
    extremum = initial_post
    previous_post = initial_post
    init = True
    progmax = False

    # A local extremum is defined by its preceding and succeeding neighbors being both greater or smaller than itself.
     # Remember that we're surveying the previous post at each step of the iteration. This means we already have access
     # to the slope coming out of our target post and only have to add a boolean for the slope of the post the step
     # before. In abstract terms, we store True if the slope is moving towards the corresponding sideline, i.e. for
     # the left channel, we are interested in latitude going down (towards ll) and for the right channel, we are
     # interested in the latitude going up (towards rr). For this, we can reuse extreme_comp.
    towards_sideline = False

    for p in posts:
        if not isoclines_established:
            longitude_intersection = linear_intersection(longitude_anchor, (p, longitude_origin))
            longitude = relative_line_position2(longitude_anchor, longitude_intersection, longitude_anchor_size)
            if not 1 > longitude > 0:
                continue
            post = p
        else:
            post, (longitude, latitude) = p

        # reminder: here we're considering overhangs
        if longitude_comp(previous_post[1][0], longitude):
            if progmax:
                continue
            else:
                if not isoclines_established:
                    latitude_intersection = linear_intersection(latitude_anchor, (p, latitude_origin))
                    latitude = relative_line_position2(latitude_anchor, latitude_intersection, latitude_anchor_size)
                    if latitude_comp(initial_post[1][1], latitude):
                        continue
                if latitude_comp(previous_post[1][1], latitude):
                    # in this case, both longitude and latitude of the new post are lower than of the previous post.
                     # However, we're already excluding the new post. Keeping the previous post means we also have to
                     # keep its slope information
                    progmax = True
                    continue

                # The cursed edge case can't be saved here either

        # reminder: here we're looking at a larger longitude value
        else:
            if progmax:
                progmax = False

            if not isoclines_established:
                latitude_intersection = linear_intersection(latitude_anchor, (p, latitude_origin))
                latitude = relative_line_position2(latitude_anchor, latitude_intersection, latitude_anchor_size)
                if latitude_comp(initial_post[1][1], latitude):
                    continue

            # This is our arena for detecting the local opposite points of the extremum (local minima for the left
             # channel which will have the global maximum as its choke point and local maxima for the right channel
             # which will have the global minimum as its choke point).


            # First, we want to know if the new post is closer to the choke point than previous_post.
            # We can accomplish this by using the extremum comparator against the previous post
            if extreme_comp(latitude, previous_post[1][1]):
                # the slope from the previous point to the new point is pointing away from the sideline which means
                 # that we need to check if we got to previous_post by moving towards the sideline. We stored this
                 # information in towards_sideline. If this boolean is True, previous_post was surrounded by two
                 # neighbors further away from the sideline, i.e. it is a valley point and can be ignored
                if towards_sideline:
                    # In order to effectively ignore a previous_post, we can't just hit continue and move on with our
                     # lives. We need to update the previous post before continuing because the new post is irrelevant,
                     # not the previous one. We have to reset towards_sideline as well since we may have moved towards
                     # previous_post from the correct direction but that doesn't mean this is also true for the new
                     # post.

                    towards_sideline = False
                    previous_post = (post, (longitude, latitude))
                    continue

                else:
                    # if only the recent side is good for a valley point we just pass and add to channel
                     # There is no need to reset towards_sideline, since that's what brought us here in the first place
                     # I'll write 'pass' to jump to the end of the iteration cycle but this could be omitted if you
                     # wanted to clean up the code.
                    pass
            elif latitude == previous_post[1][1]:
                # on a plateau, we do nothing. way too dangerous to try and catch irrelevant posts here. Possible, but
                 # I'm so fucking late with this anyway
                pass
            else:
                # we specified the plateau explicitly so we could elegantly access the opposite of the extremum
                 # comparator. In this case, we move from previous_post to new post in a promising direction so we
                 # remember that

                # if the new post is closer to the choke point than the previous post (in terms of latitude) we know
                 # that the new post cannot be a valley.
                towards_sideline = True
                # With this, we move to the end of the loop cycle


        if not init:
            if extreme_comp(previous_post[1][1], extremum[1][1]):
                extremum = previous_post
            channel.append(previous_post)
        else:
            init = False
        previous_post = (post, (longitude, latitude))
    if extreme_comp(previous_post[1][1], extremum[1][1]):
        extremum = previous_post
    channel.append(previous_post)

    return channel, extremum

# The goal line
# There are several many more versions that we could do. The very next step would be a bucket-fill approach that extends
 # the power of the valley point removal significantly. Another idea is to utilize the global maximum from the first
 # pass to determine even more fine-grained behavior.
 # The king pin would first solve the regressive overhang edge case and then introduce a "progressive warping" where the
 # rules for latitude and longitude correction change all the time. This algorithm would not need a shot path
 # construction at the end. But this is crazy. If you had this, you could interleave it with the preprocessing and have
 # another oddity: A "true linear" algorithm, meaning that you could discard the Backwards correction, interleave left
 # and right channel and finish the exercise after exactly 1 pass of all variables. Usually, you only find true linear
 # solutions for really trivial problems. I have a couple more ideas of how to throw out even more posts right off the
 # bat and one for quick-solving special cases but these are bat shit and I haven't really formalized them in my mind.


# Channel Polygon Construction Utilities

def get_anchor(alpha, omega):
    # TODO: t0 and tn can be of equal size without ll and rr being parallel if t0,tn differ in slope i.e. <= is warranted
    # TODO: Caution! This will lead to obscure errors later if alpha and omega are ever parallel and of equal size
    alpha_size = vector_magnitude(*alpha)
    omega_size = vector_magnitude(*omega)

    if alpha_size <= omega_size:
        return alpha, alpha_size
    else:
        return omega, omega_size


def vector_magnitude(p1, p2):
    # dimensional aspects are the parts of a vector, describing its change along the axes
    p1_x_aspect = p1[0] - p2[0]
    p1_y_aspect = p1[1] - p2[1]

    # aspects always form a pythagorean triangle with the magnitude of the vector as the hypotenuse
    magnitude = sqrt(p1_x_aspect ** 2 + p1_y_aspect ** 2)

    return magnitude


def linear_intersection(l1, l2):
    # generalizing the line segments into linear functions via determining their slopes and intercepts
    m_l1 = (l1[1][1] - l1[0][1]) / (l1[1][0] - l1[0][0])
    m_l2 = (l2[1][1] - l2[0][1]) / (l2[1][0] - l2[0][0])
    # print(m_l1, m_l2)

    a_l1 = l1[0][1] - (m_l1 * l1[0][0])
    a_l2 = l2[0][1] - (m_l2 * l2[0][0])

    # linear functions take the form of y=mx+a, we can equalize both, simplify and solve for x
    origin_x = ((a_l1 - a_l2) / (m_l2 - m_l1))

    # and use one of the original functions (derived from slope, intercept and form above) to construct the y coordinate
    origin_y = m_l1 * origin_x + a_l1
    origin = (origin_x, origin_y)
    return origin


def relative_line_position2(anchor, target, anchor_size):
    # We revise the function to return 0 if the value would be lower than 0 and 1 if it would be larger than one. The
    # posts in question lie outside of the channel polygon

    anchor_l, anchor_r = anchor

    # if the target is one of the anchor posts, you can set the reading to 0 or 1
    if target == anchor_l:
        return 0
    elif target == anchor_r:
        return 1

    elif (anchor_l[0] <= target[0] <= anchor_r[0] or anchor_r[0] <= target[0] <= anchor_l[0] and
          anchor_l[1] <= target[1] <= anchor_r[1] or anchor_r[1] <= target[1] <= anchor_l[1]):
        pass

    # if the target has a lower value for x than the left anchor post, it lies outside of the anchor and closer to the
    # left anchor post, i.e. the relative line position would be lower than 0 so we set it to -1 (~before the anchor,
    # arbitrarily lower than 0)
    elif target[0] <= anchor_l[0] <= anchor_r[0]:
        return -1

    # the first two cases looked at all cases where the target one of the anchor posts and the third case caught all
    # posts that lie before it. The only remaining option is for the target to lie behind the anchor (in terms of the
    # anchor as an interval on a linear function. We constructed the target using linear_intersection() so we know it
    # is on this theoretical "anchor-function"), we set it to 2 (~behind, arbitrarily higher than 1)
    else:
        return 2

    d_vec = vector_magnitude(anchor[0], target)
    if d_vec < 0 or d_vec > anchor_size:
        raise ValueError("failed sanity check, vector out of bounds")
    else:
        return d_vec / anchor_size


# Channel Polygon Evaluation

## IMPORTANT: THIS HAS BEEN CHANGED! EVERY POST NOW HAS THE SHAPE ((x, y), (longitude, latitude))
def sanity_checks(choke_left, choke_right):
    # Wir erhalten also zwei Listen von Channels und die jeweiligen Choke Points. Wir machen erstmal ein paar Sanity
    # Checks, ob irgendwas ganz schlimm schiefgegangen ist. Hier werten wir die Isoklinenwerte aus. Generell sind die
    # Koordinaten nur noch zum Plotten interessant, für alle Proportionen benutzen wir die Isoklinen.

    indicator = 0

    # Kein echter Choke Point. Nicht illegal, aber seltsam
    if choke_left[1][0] == 0:
        print(
            "Suspicious choke point configuration, couldn't find any left goal post inside of the channel polygon")
        indicator = 1

    # Dasselbe in Rot; again, nicht verboten, aber was war hier los?
    if choke_right[1][0] == 1:
        print(
            "Suspicious choke point configuration, couldn't find any right goal posts inside of the channel polygon")
        indicator = 1

    # Jetzt wird's kritisch. Wenn der linke Choke Point kleiner als 0 oder der rechte größer als 1 ist, haben wir
    # irgendwie Anti-Choke Points außerhalb des Kanalpolygons zugelassen. Das darf eigentlich nicht passieren
    if any([choke_left[1][0] < 0 or choke_right[1][0] > 1]):
        raise ValueError("critical value error, illegal values for choke points; results no longer meaningful")

    # Hat ein linker Torpfosten eine Latitude größer als 1 liegt er auf der falschen Seite außerhalb des Kanalpolygons.
    # Das heißt, die Scheiße ist nichtmehr lösbar. Wir können hier also abbrechen. Das ist der Fall bei Aufgabe 2.
    # Diesen Umstand könnte man theoretisch auch im Preprocessing einfangen, spielt aber keine große Rolle.
    if any([choke_left[1][1] > 1 or choke_right[1][1] < 0]):
        warnings.warn("Choke Point too extreme!, crosses channel boundary, task not solvable")
        indicator = 1

    # Hier könnte noch ein Test stehen, der schaut, ob beide Channel-Linien sich im jetzigen Zustand kreuzen. Wenn das
    # der Fall ist, ist das Problem ebenfalls nicht lösbar; indicator = 1

    # Hier könnte auch noch ein Test stehen, ob die beiden Choke Points dieselbe Longitude aber überlappende Latitude
    # haben. Wenn das der Fall ist, ist das Problem nicht lösbar; indicator = 1

    return indicator

## IMPORTANT: THIS HAS BEEN CHANGED! EVERY POST NOW HAS THE SHAPE ((x, y), (longitude, latitude))
def get_channel_configuration(t0, tn, left_channel, right_channel, choke_left, choke_right, verbose=False):
    # What is the alignment of the two choke points? l (= the left choke point is closer to t0), r (= the right choke
     # point is closer to t0), x (both choke points are equal in longitude)
    # First, we want to know the structural properties of the channel polygon. This includes:
     # Is the channel broad (both choke points leave a gap) or narrow (the choke points "overlap" in latitude). We have
      # an overlap in latitude if the left choke point has a larger latitude than the right choke point. In this case,
      # we can only shoot across the diagonal of the channel. If we have to shoot from t0-left towards tn-right or from
      # t0-right towards tn-left is determined by the next question.
     # Which goal is shorter? t0 if the vector given by the two posts has a lower magnitude, tn if this is the case for
      # tn, and x if both are equal. The value is stored as along with, first, the shorter and then the larger
      # magnitude examples: (t0, (magnitude_t0, magnitude_tn)), (tn, (magnitude_tn, magnitude_t0)). If we stored the
      # magnitudes in the standard order (tn, t0) we lose the ability to abstract the code, i.e. we will have to check
      # the variable multiple times explicitly. This way, we know where the smaller number is and have a more abstract
      # (read: adaptable) variable in the shape of (shorter_goal, (shorter_goal_magnitude, other_goal_magnitude)). If
      # both are equal, we take t0

    # If the choke points do not overlap, a shot path along the latitude isoclines exists. However, a leftwards_tilt cannot be
     # established, since both are theoretically possible.
    if choke_left[1][1] < choke_right[1][1]:
        broad = True
    else:
        broad = False
        # If the choke points overlap, there is no shot path along the latitude isoclines and a predictable leftwards_tilt of the
         # channel from the opposite side of the first choke point (i.e. lower latitude) to the second coke point
         # emerges.

        # If the left choke point has a lower longitude than the right choke point, any shot path has to start closer
         # to t0_l and end closer to tn_r.
    if choke_left[1][0] < choke_right[1][0]:
        leftwards_tilt = True
    elif choke_left[1][0] > choke_right[1][0]:
        leftwards_tilt = False
    else:
        leftwards_tilt = None
        if not broad:
            # If both choke points overlap in latitude but match in longitude, the problem is no longer solvable
            warnings.warn("Critial Value Error, choke points overlap at equal longitude")

    t0_size = vector_magnitude(*t0)
    tn_size = vector_magnitude(*tn)
    if t0_size < tn_size:
        t0_pinch = True
    elif t0_size > tn_size:
        t0_pinch = False
    else:
        t0_pinch = None

    if verbose:
        print(f"{"Broad" if broad else "Narrow"} channel polygon configuration "
              f"with {"equal size goals" if t0_pinch is None else f"pinch at {"t0" if t0_pinch else "tn"}."}"
              f"{"" if leftwards_tilt is None else f" The channel goes from {"right to left." if leftwards_tilt else "left to right."}"}")

    return broad, leftwards_tilt, t0_pinch
