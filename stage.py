class Stage:
    def __init__(self, terrain, gravity):
        self.terrain = terrain
        self.gravity = gravity
        self.soldiers = []

    def update(self):
        for soldier in self.soldiers:
            soldier.update_position(self.terrain, self.gravity)