import numpy as np
import sympy as sp


def calculate_shot_path(parallels):
    (P1, P2), (P3, P4) = parallels
    # Berechne die Mittelpunkte der korrespondierenden Endpunkte
    M1 = sp.Point2D((P1.x + P3.x) / 2, (P1.y + P3.y) / 2)
    M2 = sp.Point2D((P2.x + P4.x) / 2, (P2.y + P4.y) / 2)

    return sp.Segment2D(M1, M2)


def test_orientation(goal1, goal2):
    intersection_point1 = intersection(goal1[0], goal2[0], goal1[1], goal2[1])
    intersection_point2 = intersection(goal1[0], goal2[1], goal1[1], goal2[0])

    return_values = []

    if not intersection_point1:
        l0 = goal1[0]
        r0 = goal1[1]
        l1 = goal2[0]
        r1 = goal2[1]
        return_values.append([l0, r0, l1, r1])

    if not intersection_point2:
        l0 = goal1[0]
        r0 = goal1[1]
        l1 = goal2[1]
        r1 = goal2[0]
        return_values.append([l0, r0, l1, r1])

    return return_values


def intersection(p1, p2, q1, q2):
    # https://www.youtube.com/watch?v=bvlIYX9cgls
    # this function checks if two given line segments have an intersection point and if they do, it calculates it

    p1x, p1y = p1
    p2x, p2y = p2
    q1x, q1y = q1
    q2x, q2y = q2

    # define vector p and q
    p = (p2x - p1x, p2y - p1y)
    q = (q2x - q1x, q2y - q1y)

    # any point on vector p: p1 + αp    α is any value between 0 and 1
    # same goes for vector q

    a = (q2x - q1x) * (q1y - p1y) - (q2y - q1y) * (q1x - p1x)
    c = (p2x - p1x) * (q1y - p1y) - (p2y - p1y) * (q1x - p1x)
    b = (q2x - q1x) * (p2y - p1y) - (q2y - q1y) * (p2x - p1x)

    if b == 0:  # Parallel or collinear
        if a == 0 and c == 0:  # Collinear
            # Check if the two line segments overlap
            def is_between(a, b, c):
                return min(a, b) <= c <= max(a, b)

            if (
                    is_between(p1x, p2x, q1x) and is_between(p1y, p2y, q1y) or
                    is_between(p1x, p2x, q2x) and is_between(p1y, p2y, q2y) or
                    is_between(q1x, q2x, p1x) and is_between(q1y, q2y, p1y) or
                    is_between(q1x, q2x, p2x) and is_between(q1y, q2y, p2y)
            ):
                raise Exception("Line segments are collinear and overlapping!")
            else:
                return None  # Collinear but disjoint
        else:
            return None  # Parallel but not collinear

    # Compute intersection point using parametric equations
    alpha = a / b
    beta = c / b
    if 0 <= alpha <= 1 and 0 <= beta <= 1:
        x0 = p1x + alpha * p[0]
        y0 = p1y + alpha * p[1]
        return x0, y0
    else:
        return None  # Intersection not within segment bounds


def perpendicularIntersectionPoint(line, c):
    # habe ich nicht zu 100 % verstanden, und war zu faul mir das nochmal genau anzuschauen :)
    # t ist die Position des von c nächsten Punktes P auf der Strecke AB
    # damit kann der Schnittpunkt berechnet werden

    ax, ay = line[0]
    bx, by = line[1]
    cx, cy = c

    ab = np.array([bx - ax, by - ay])

    ab_normal = np.array([-ab[1], ab[0]])

    t = ((cx - ax) * ab[0] + (cy - ay) * ab[1]) / (ab[0]**2 + ab[1]**2)

    intersectionPoint = np.array([ax, ay]) + t * ab

    return float(intersectionPoint[0]), float(intersectionPoint[1])


def crossProduct(line, point):
    # https://stackoverflow.com/questions/3838319/how-can-i-check-if-a-point-is-below-a-line-or-not
    # das Ergebnis der Funktion ist von der Reihenfolge der Punkte der Linie abhängig!
    # Das Cross Product der zwei Vektoren ist positiv, wenn der Punkt auf der einen Seite der Strecke ist und negativ,
    # wenn der Punkt auf der anderen Seite ist

    x1, y1 = line[0]
    x2, y2 = line[1]
    xPoint, yPoint = point
    v1 = (x2 - x1, y2 - y1)
    v2 = (x2 - xPoint, y2 - yPoint)
    xp = (v1[0] * v2[1]) - (v1[1] * v2[0])

    return xp


def lengthVector(line):
    # https://www.statology.org/how-calculate-length-magnitude-vector-python/
    a = line[0]
    b = line[1]

    vector = np.array([b[0] - a[0], b[1] - a[1]])

    magnitude = np.linalg.norm(vector)

    return float(magnitude)
