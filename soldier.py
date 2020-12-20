import math
import vector
import polygon
import collision

class Soldier:
    def __init__(self, position, width, walking_speed, hitpoints, gun):
        self.position = position
        self.width = width
        feet = [vector.Vector(self.position.x - self.width / 2, self.position.y), vector.Vector(self.position.x + self.width / 2, self.position.y)]
        self.standing_rectangle = polygon.Polygon(feet + [vector.Vector(self.position.x + self.width / 2, self.position.y - self.width * 2), vector.Vector(self.position.x - self.width / 2, self.position.y - self.width * 2)])
        self.crouched_rectangle = polygon.Polygon(feet + [vector.Vector(self.position.x + self.width / 2, self.position.y - self.width), vector.Vector(self.position.x - self.width / 2, self.position.y - self.width)])
        self.crouched = False
        self.rotation = 0
        self.velocity = vector.Vector(0, 0)
        self.grounded = None
        self.hitpoints = hitpoints
        self.walking_speed = walking_speed
        self.gun = gun
        self.heading = 0
    
    def update_position(self, terrain, gravity):
        if self.grounded is None:
            #apply gravity and horizontal movement to velocity
            if self.velocity.y < 5:
                self.velocity = vector.Vector(self.heading * self.walking_speed, self.velocity.y + gravity)
            else:
                self.velocity = vector.Vector(self.heading * self.walking_speed, self.velocity.y)

            #create modified_velocity
            modified_velocity = self.velocity
            landed = False
            
            #check all terrain for air collision
            for i, chunk in enumerate(terrain): # MIGHT ADD THE FURTHER ITERATION THING
                result = collision.air_collision(self.standing_rectangle, chunk.poly, self.velocity)

                #if collision
                if result[0]:
                    #if valid ground
                    if chunk.ground:
                        landed = self.land(terrain, i, modified_velocity, result[1])
                        if landed:
                            break
                    else:
                        modified_velocity += result[1]
            if not landed:
                self.translate(modified_velocity)

        #compare position + velocity to endpoint of ground

        #if position past a connected end
            #split velocity into before and after
            #check for collision and move before (stop after any of these steps if collision)
            #check for collision and rotate
            #if we get to rotate set grounded to new ground
            #check for collision and move after
        #if position past an edge + half width
            #split velocity into before and after
            #check for collision and move before (stop after any of these steps if collision)
            #check for collision and rotate
            #if we get to rotate set grounded to None
            #check for collision and move after
    
    def land(self, terrain, i, modified_velocity, translation_vector):
        chunk = terrain[i]

        modified_velocity += translation_vector

        #set to_ground to None
        to_ground = None
        
        # !!! this whole business might not work on vertical ledges !!!
        # add repeated checking after a collision until it collides with nothing (watch out for "just on edge" being a trigger)

        #create a vector representing the ground
        ground_edge = chunk.poly.points[1] - chunk.poly.points[0]
        # determine the sign of the slope of ground (ground will always be left to right)
        if chunk.poly.points[1].y >= chunk.poly.points[0].y and collision.side(chunk.poly.points[1], chunk.poly.points[0], self.standing_rectangle.points[3] + modified_velocity) > 0: #might have to flip
            #if left foot within ground x
            if chunk.poly.points[0].x <= self.standing_rectangle.points[0].x + modified_velocity.x <= chunk.poly.points[1].x:
                #if connection to the right and position after rotate will be off ground
                if chunk.connect_right and self.standing_rectangle.points[0].x + modified_velocity.x + ground_edge.normalize().x * self.width / 2 > chunk.poly.points[1].x:
                    #keep falling - no adjustment
                    modified_velocity -= translation_vector
                else:
                    #flip as normal
                    to_ground = i
                    origin = self.standing_rectangle.points[0] + modified_velocity
                    self.rotation = math.acos(vector.Vector(1, 0).dot(ground_edge) / ground_edge.get_magnitude())
            # if right foot within ground x
            elif chunk.poly.points[0].x <= self.standing_rectangle.points[1].x + modified_velocity.x <= chunk.poly.points[1].x:
                #flip around left end of ground
                origin = chunk.poly.points[0]
                # connection to the left and position after rotate will be off ground
                if chunk.connect_left and self.position.x + modified_velocity.x < chunk.poly.points[0].x: #changed this might have broken
                    #flip onto left connect
                    to_ground = i - 1
                    connect_edge = terrain[to_ground].poly.points[1] - terrain[to_ground].poly.points[0]
                    self.rotation = math.acos(vector.Vector(1, 0).dot(connect_edge) / connect_edge.get_magnitude())
                    if terrain[to_ground].poly.points[1].y < terrain[to_ground].poly.points[0].y:
                        self.rotation = self.rotation * -1
                else:
                    #flip onto ground
                    to_ground =  i
                    self.rotation = math.acos(vector.Vector(1, 0).dot(ground_edge) / ground_edge.get_magnitude())
        elif collision.side(chunk.poly.points[1], chunk.poly.points[0], self.standing_rectangle.points[2] + modified_velocity) > 0: #might have to flip
            if chunk.poly.points[0].x <= self.standing_rectangle.points[1].x + modified_velocity.x <= chunk.poly.points[1].x:
                if chunk.connect_left and self.standing_rectangle.points[1].x + modified_velocity.x - ground_edge.normalize().x * self.width / 2 < chunk.poly.points[0].x:
                    #keep falling - no adjustment
                    modified_velocity -= translation_vector
                else:
                    #flip as normal
                    to_ground = i
                    origin = self.standing_rectangle.points[1] + modified_velocity
                    self.rotation = -1 * math.acos(vector.Vector(1, 0).dot(ground_edge) / ground_edge.get_magnitude())
            elif chunk.poly.points[0].x <= self.standing_rectangle.points[0].x + modified_velocity.x <= chunk.poly.points[1].x:
                #flip around right end of ground
                origin = chunk.poly.points[1]
                if chunk.connect_right and self.position.x + modified_velocity.x >= chunk.poly.points[1].x: #changed this might have broken
                    #flip onto right connect
                    to_ground = i + 1
                    connect_edge = terrain[to_ground].poly.points[1] - terrain[to_ground].poly.points[0]
                    self.rotation = math.acos(vector.Vector(1, 0).dot(connect_edge) / connect_edge.get_magnitude())
                    if terrain[to_ground].poly.points[1].y < terrain[to_ground].poly.points[0].y:
                        self.rotation = self.rotation * -1
                else:
                    #flip onto ground
                    to_ground = i
                    self.rotation = -1 * math.acos(vector.Vector(1, 0).dot(ground_edge) / ground_edge.get_magnitude())

        # land or dont land depending on results (set rotation and grounded and zero velocity) be sure to check collision on rotate (if collision dont rotate or land)
        if to_ground is not None:
            
            self.translate(modified_velocity) #this is weird think about this

            self.standing_rectangle.rotate(origin, self.rotation)
            stop = False
            for k, secondary_chunk in enumerate(terrain):
                if k == to_ground or terrain[to_ground].connect_left and k + 1 == to_ground or terrain[to_ground].connect_right and k - 1 == to_ground:
                    pass
                elif collision.air_collision(self.standing_rectangle, secondary_chunk.poly, vector.Vector(0, 0))[0]:
                        self.standing_rectangle.rotate(origin, -1 * self.rotation)
                        self.rotation = 0
                        stop = True
                        break
            if not stop:
                self.grounded = to_ground
                self.velocity = vector.Vector(0, 0)
                self.crouched_rectangle.rotate(origin, self.rotation)
                self.position = self.position.rotate(origin, self.rotation)
                return True
            
            self.translate(modified_velocity * -1)

        return False


    def translate(self, velocity):
        self.position += velocity
        self.standing_rectangle.translate(velocity)
        self.crouched_rectangle.translate(velocity)
    
    def jump(self):
        pass
