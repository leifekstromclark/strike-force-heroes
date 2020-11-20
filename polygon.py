import vector

class Polygon:
    def __init__(self, points):
        self.points = points
        self.center = self.get_center()

    def get_center(self):
        return vector.Vector(sum([point.x for point in self.points]), sum([point.y for point in self.points])) / len(self.points)
    
    def translate(self, vector):
        for i in range(len(self.points)):
            self.points[i] += vector
        self.center = self.get_center()
