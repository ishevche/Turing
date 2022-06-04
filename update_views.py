from math import sin, cos, pi, tan

import constants


def update_view_walls(my_coords, view_data, start_angle, end_angle):
    angle = (start_angle - end_angle) / (constants.EYES_AMOUNT - 1)
    for i in range(constants.EYES_AMOUNT):
        x_2 = (constants.VIEW_DISTANCE * cos(start_angle - angle * i)
               + my_coords[0])
        y_2 = (constants.VIEW_DISTANCE * sin(start_angle - angle * i)
               + my_coords[1])
        if not -1 < x_2 < 101 or not -1 < y_2 < 101:
            length = wall_dist(my_coords, (x_2, y_2),
                               start_angle - angle * i)
            if length < view_data[i][0]:
                view_data[i][0] = length
                view_data[i][1] = 1


def update_views(my_coords, other_coords, view_data, start_angle, end_angle,
                 data):
    angle = (start_angle - end_angle) / (constants.EYES_AMOUNT - 1)
    for i in range(constants.EYES_AMOUNT):
        x_2 = (constants.VIEW_DISTANCE * cos(start_angle - angle * i)
               + my_coords[0])
        y_2 = (constants.VIEW_DISTANCE * sin(start_angle - angle * i)
               + my_coords[1])
        length = circle_dist(other_coords, my_coords,
                             (x_2, y_2), constants.RADIUS)
        if length < view_data[i][0]:
            view_data[i][0] = length
            view_data[i][1] = data


def distance(point_1, point_2):
    x_1, y_1 = point_1
    x_2, y_2 = point_2
    dist = ((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2) ** (1 / 2)
    return dist


def intersect_check(centre, point_a, point_b, radius):
    x, y = centre
    x_1, y_1 = point_a
    x_2, y_2 = point_b
    x_1 -= x
    y_1 -= y
    x_2 -= x
    y_2 -= y
    c = x_1 * y_2 - x_2 * y_1
    dist = distance(point_a, point_b)
    check = radius ** 2 * dist ** 2 - c ** 2
    return check >= 0


def sgn(number):
    if number < 0:
        return -1
    return 1


def intersections(centre, point_a, point_b, radius):
    x, y = centre
    x_1, y_1 = point_a
    x_2, y_2 = point_b
    x_1 -= x
    y_1 -= y
    x_2 -= x
    y_2 -= y
    a = x_2 - x_1
    b = y_2 - y_1
    dist = distance(point_a, point_b)
    c = x_1 * y_2 - x_2 * y_1
    intersect_x_1 = (c * b + sgn(b) * a *
                     (radius ** 2 * dist ** 2 - c ** 2) ** (1 / 2)) / (
                            dist ** 2) + x
    intersect_y_1 = (-1 * c * a + abs(b) *
                     (radius ** 2 * dist ** 2 - c ** 2) ** (1 / 2)) / (
                            dist ** 2) + y
    intersect_x_2 = (c * b - sgn(b) * a *
                     (radius ** 2 * dist ** 2 - c ** 2) ** (1 / 2)) / (
                            dist ** 2) + x
    intersect_y_2 = (-1 * c * a - abs(b) *
                     (radius ** 2 * dist ** 2 - c ** 2) ** (1 / 2)) / (
                            dist ** 2) + y
    return (intersect_x_1, intersect_y_1), (intersect_x_2, intersect_y_2)


def circle_dist(centre, point_a, point_b, radius):
    if not intersect_check(centre, point_a, point_b, radius):
        return distance(point_a, point_b)
    intersect_1, intersect_2 = intersections(centre, point_a, point_b, radius)
    if distance(intersect_1, point_a) < distance(intersect_2, point_a):
        if not (point_a[0] < intersect_1[0] < point_b[0] or
                point_b[0] < intersect_1[0] < point_a[0]):
            return distance(point_a, point_b)
        if not (point_a[1] < intersect_1[1] < point_b[1] or
                point_b[1] < intersect_1[1] < point_a[1]):
            return distance(point_a, point_b)
        return distance(intersect_1, point_a)
    else:
        if not (point_a[0] < intersect_2[0] < point_b[0] or
                point_b[0] < intersect_2[0] < point_a[0]):
            return distance(point_a, point_b)
        if not (point_a[1] < intersect_2[1] < point_b[1] or
                point_b[1] < intersect_2[1] < point_a[1]):
            return distance(point_a, point_b)
        return distance(intersect_2, point_a)


def wall_dist(point_a, point_b, angle):
    x_1 = point_a[0]
    y_1 = point_a[1]
    x_2 = point_b[0]
    y_2 = point_b[1]
    if not -1 < y_2 < 101 and not -1 < x_2 < 101:
        if x_2 <= -1 and y_2 <= -1:
            if x_2 < y_2:
                wall_x = -1
                if angle % pi != pi / 2:
                    wall_y = tan(angle) * (wall_x - x_1) + y_1
                else:
                    wall_y = y_1
            else:
                wall_y = -1
                if angle % pi != pi / 2:
                    wall_x = (wall_y - y_1) / tan(angle) + x_1
                else:
                    wall_x = x_1
            return distance((wall_x, wall_y), (x_1, y_1))
        if x_2 >= 101 and y_2 >= 101:
            if x_2 > y_2:
                wall_x = 101
                if angle % pi != pi / 2:
                    wall_y = tan(angle) * (wall_x - x_1) + y_1
                else:
                    wall_y = y_1
            else:
                wall_y = 101
                if angle % pi != pi / 2:
                    wall_x = (wall_y - y_1) / tan(angle) + x_1
                else:
                    wall_x = x_1
            return distance((wall_x, wall_y), (x_1, y_1))
        if x_2 <= -1 and y_2 >= 101:
            if x_2 + 1 > y_2 - 101:
                wall_x = -1
                if angle % pi != pi / 2:
                    wall_y = tan(angle) * (wall_x - x_1) + y_1
                else:
                    wall_y = y_1
            else:
                wall_y = 101
                if angle % pi != pi / 2:
                    wall_x = (wall_y - y_1) / tan(angle) + x_1
                else:
                    wall_x = x_1
            return distance((wall_x, wall_y), (x_1, y_1))
        if x_2 >= 101 and y_2 <= -1:
            if x_2 - 101 > y_2 + 1:
                wall_x = 101
                if angle % pi != pi / 2:
                    wall_y = tan(angle) * (wall_x - x_1) + y_1
                else:
                    wall_y = y_1
            else:
                wall_y = -1
                if angle % pi != pi / 2:
                    wall_x = (wall_y - y_1) / tan(angle) + x_1
                else:
                    wall_x = x_1
            return distance((wall_x, wall_y), (x_1, y_1))
    if -1 < y_2 < 101:
        if x_2 < -1:
            wall_x = -1
            if angle % pi != pi / 2:
                wall_y = tan(angle) * (wall_x - x_1) + y_1
            else:
                wall_y = y_1
        else:
            wall_x = 101
            if angle % pi != pi / 2:
                wall_y = tan(angle) * (wall_x - x_1) + y_1
            else:
                wall_y = y_1
        return distance((wall_x, wall_y), (x_1, y_1))
    if -1 < x_2 < 101:
        if y_2 <= -1:
            wall_y = -1
            if angle % pi != pi / 2:
                wall_x = (wall_y - y_1) / tan(angle) + x_1
            else:
                wall_x = x_1
        else:
            wall_y = 101
            if angle % pi != pi / 2:
                wall_x = (wall_y - y_1) / tan(angle) + x_1
            else:
                wall_x = x_1
        return distance((wall_x, wall_y), (x_1, y_1))
