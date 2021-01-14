import vector
import polygon

'''
Project a set of points on an axis.
Take a normalized vector representing an axis and a set of points.
Return the overall projection as an interval.
'''
def project_points(axis, points):

    #Iterate through points
    minimum = None
    maximum = None
    for point in points:

        #Take the dot product of the point and the axis (This accurately represents the point's location on the axis because we normalized the axis earlier).
        dot_product = axis.dot(point)

        #Update the minimum and maximum of the interval representing the projection as necessary.
        if minimum is None:
            minimum = dot_product
            maximum = dot_product
        elif dot_product < minimum:
            minimum = dot_product
        elif dot_product > maximum:
            maximum = dot_product
    
    return minimum, maximum

'''
Calculate the distance between two intervals.
Take two intervals represented by maximums and minimums.
Return the distance between the intervals (It will be negative if they overlap).
'''
def get_interval_distance(minimum_a, maximum_a, minimum_b, maximum_b):
    dist_a = minimum_a - maximum_b
    dist_b = minimum_b - maximum_a

    if abs(dist_a) < abs(dist_b):
        return dist_a
    return dist_b


'''
Detect a collision between two convex polygons and return a translation vector that will slide them.
This will be used for soldiers moving through the air.
Take two polygons.
Return a boolean representing intersection and a translation vector if needed.
'''
def air_collision(polygon_a, polygon_b):

    min_interval_distance = None

    #Iterate through indices of points in both polygons.
    num_points_a = len(polygon_a.points)
    num_points_b = len(polygon_b.points)

    for i in range(num_points_a + num_points_b):
        
        #Create a vector representing an axis perpendicular to the edge between the ith point and the i+1th point.
        if i < num_points_a:
            inc = (i + 1) % num_points_a
            axis = vector.Vector(-1 * (polygon_a.points[inc].y - polygon_a.points[i].y), polygon_a.points[inc].x - polygon_a.points[i].x)

        else:
            i -= num_points_a
            inc = (i + 1) % num_points_b
            axis = vector.Vector(-1 * (polygon_b.points[inc].y - polygon_b.points[i].y), polygon_b.points[inc].x - polygon_b.points[i].x)
        
        #Normalize the vector representing the axis.
        axis = axis.normalize()

        #Project both polygons on the axis.
        minimum_a, maximum_a = project_points(axis, polygon_a.points)
        minimum_b, maximum_b = project_points(axis, polygon_b.points)

        #If the intervals do not overlap the polygons do not intersect during the move.
        interval_distance = get_interval_distance(minimum_a, maximum_a, minimum_b, maximum_b)
        if interval_distance > 0:
            return (False,)
        
        #If the interval distance is the smallest so far store it as well as the axis (flip if needed).
        interval_distance = abs(interval_distance)
        if min_interval_distance is None or interval_distance < min_interval_distance:
            min_interval_distance = interval_distance
            translation_axis = axis

            if translation_axis.dot(polygon_a.center - polygon_b.center) < 0:
                translation_axis = translation_axis * -1

    return (True, translation_axis * min_interval_distance)

'''
Finds coefficients of linear equation.
Takes two points.
Returns coefficients of the linear equation that passes through them. (Constant on other side).
'''
def points_to_coefficients(p1, p2):
    a = p1.y - p2.y
    b = p2.x - p1.x
    c = p1.x * p2.y - p2.x * p1.y
    return a, b, -c

'''
Use Cramer's Rule to determine the intersection of two lines.
Takes two sets of coefficients of linear equations (Constants on other side).
Returns an intersection if there there is a unique solution.
'''
def intersect(co1, co2):
    det  = co1[0] * co2[1] - co1[1] * co2[0]
    det_x = co1[2] * co2[1] - co1[1] * co2[2]
    det_y = co1[0] * co2[2] - co1[2] * co2[0]
    if det != 0:
        x = det_x / det
        y = det_y / det
        return vector.Vector(x, y)
    else:
        return False

'''
Uses a crossproduct to determine what side of a line a point is on.
Takes three points.
Returns a negative number or a positive number or zero depending on the position of the third point compared to the first two.
'''
def side(p1, p2, p3):
    return (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x)

'''
Detect a collision between a convex polygon and a rectangle moving along the same axis as its base and return a translation vector along that same axis.
This will be used for players moving along the ground.
Take a polygon, a rectangle, and a velocity. The first and second points in the rectangle should be on the base or top.
Return a boolean representing intersection and a translation vector if needed.
'''
def grounded_collision(rectangle, poly, velocity):

    #Create a list of points on the polygon consisting of all intersections with and vertices between the lines formed by the base and the top of the rectangle
    to_project = []
    base_co1 = points_to_coefficients(rectangle.points[0], rectangle.points[1])
    base_co2 = points_to_coefficients(rectangle.points[2], rectangle.points[3])
    num_points = len(poly.points)
    for i in range(num_points):
        side_1 = side(rectangle.points[0], rectangle.points[1], poly.points[i])
        side_2 = side(rectangle.points[2], rectangle.points[3], poly.points[i])
        if (side_1 <= 0 and side_2 <= 0) or (side_1 >= 0 and side_2 >= 0):
            to_project.append(poly.points[i])
        
        inc = (i + 1) % num_points
        co = points_to_coefficients(poly.points[inc], poly.points[i])
        base_int = intersect(base_co1, co)
        if base_int:
            base_int = base_int.round()
            if min(poly.points[inc].x, poly.points[i].x) <= base_int.x <= max(poly.points[inc].x, poly.points[i].x) and min(poly.points[inc].y, poly.points[i].y) <= base_int.y <= max(poly.points[inc].y, poly.points[i].y):
                to_project.append(base_int)
        base_int = intersect(base_co2, co)
        if base_int:
            base_int = base_int.round()
            if min(poly.points[inc].x, poly.points[i].x) <= base_int.x <= max(poly.points[inc].x, poly.points[i].x) and min(poly.points[inc].y, poly.points[i].y) <= base_int.y <= max(poly.points[inc].y, poly.points[i].y):
                to_project.append(base_int)
    
    if len(to_project) > 0:
        axis = (rectangle.points[1] - rectangle.points[0]).normalize()

        minimum_poly, maximum_poly = project_points(axis, to_project)
        minimum_rect, maximum_rect = project_points(axis, (rectangle.points[0], rectangle.points[1]))

        velocity_projection = axis.dot(velocity)

        if velocity_projection < 0:
            minimum_rect += velocity_projection
        else:
            maximum_rect += velocity_projection
        
        interval_distance = get_interval_distance(minimum_rect, maximum_rect, minimum_poly, maximum_poly)

        if interval_distance > 0:
            return (False,)
        
        interval_distance = abs(interval_distance)

        if velocity.x > 0:
            axis = axis * -1
        
        return (True, axis * interval_distance)
    return (False,)