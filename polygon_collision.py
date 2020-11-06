import vector
import polygon

'''
Project a polygon on an axis.
Take a normalized vector representing an axis and a polygon.
Return the projection as an interval.
'''
def project_polygon(axis, poly):

    #Iterate through points in the polygon
    minimum = False
    for point in poly.points:

        #Take the dot product of the point and the axis (This accurately represents the point's location on the axis because we normalized the axis earlier).
        dot_product = axis.dot(point)

        #Update the minimum and maximum of the interval representing the projection as necessary.
        if not minimum:
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
def interval_distance(minimum_a, maximum_a, minimum_b, maximum_b):
    if minimum_a < minimum_b:
        return minimum_b - maximum_a
    else:
        return minimum_a - maximum_b


'''
Detect a collision between two convex polygons.
Take two polygons and a relative velocity.
Return a boolean representing intersection and a translation vector if needed.
'''
def polygon_collision(polygon_a, polygon_b, velocity):
    
    intersect = True
    min_interval_distance = False

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
        minimum_a, maximum_a = project_polygon(axis, polygon_a)
        minimum_b, maximum_b = project_polygon(axis, polygon_b)

        #Project the velocity vector on the axis (See project_polygon).
        velocity_projection = axis.dot(velocity)

        #Add the velocity projection on the end of the interval of polygon_a's projection. This new interval will represent the interval spanned over the duration of motion.
        if velocity_projection < 0:
            minimum_a += velocity_projection
        else:
            maximum_a += velocity_projection

        #If the intervals do not overlap the polygons do not intersect during the move.
        interval_distance = interval_distance(minimum_a, maximum_a, minimum_b, maximum_b)
        if interval_distance > 0:
            intersect = False
            break
        
        #If the interval distance is the smallest so far store it as well as the axis (flip if needed).
        interval_distance = abs(interval_distance)
        if not min_interval_distance or interval_distance < min_interval_distance:
            min_interval_distance = interval_distance
            translation_axis = axis

            if translation_axis.dot(polygon_a.center - polygon_b.center) < 0:
                translation_axis = -1 * translation_axis

    #Return
    if intersect:
        return True, translation_axis * min_interval_distance
    return False