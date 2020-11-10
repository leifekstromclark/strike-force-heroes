class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._magnitude = -1

    def get_magnitude(self):
        if self._magnitude == -1:
            self._magnitude = (self.x ** 2 + self.y ** 2) ** 0.5
        return self._magnitude

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)
    
    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other)
    
    def __floordiv__(self, other):
        return Vector(self.x // other, self.y // other)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def normalize(self):
        return self / self.get_magnitude()
    
    def int(self):
        return Vector(int(self.x), int(self.y))