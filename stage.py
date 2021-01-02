class Stage:
    def __init__(self, terrain, gravity, terminal_velocity):
        self.terrain = terrain
        self.gravity = gravity
        self.terminal_velocity = terminal_velocity
        self.soldiers = []

    def update(self):
        for soldier in self.soldiers:
            soldier.update_position(self.terrain, self.gravity, self.terminal_velocity)