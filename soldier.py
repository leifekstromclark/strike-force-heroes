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
        self.jumped = False
    
    def update_position(self, terrain, gravity, terminal_velocity):
        
        previous = None
        if self.jumped:
            result = self.jump(terrain)
            if result[0]:
                previous = result[1]
            self.jumped = False

        if self.grounded is None:
            #apply gravity and horizontal movement to velocity
            if self.velocity.y < terminal_velocity:
                self.velocity = vector.Vector(self.heading * self.walking_speed, self.velocity.y + gravity)
            else:
                self.velocity = vector.Vector(self.heading * self.walking_speed, self.velocity.y)

            #create modified_velocity
            self.velocity
            landed = False
            negations = [0]
            
            self.translate(self.velocity)
            #check all terrain for air collision
            for i, chunk in enumerate(terrain): # MIGHT ADD THE FURTHER ITERATION THING
                if i != previous:

                    result = collision.air_collision(self.standing_rectangle, chunk.poly)

                    #if collision
                    if result[0]:
                        self.translate(result[1])
                        #if valid ground
                        if chunk.ground:
                            landed = self.land(terrain, i, result[1])
                            if landed:
                                break
                        if result[1].get_magnitude() != 0:
                            negations.append(math.sin(math.acos(vector.Vector(1, 0).dot(result[1]) / result[1].get_magnitude())))
            
            if not landed:
                if self.velocity.y < 0:
                    self.velocity -= vector.Vector(0, self.velocity.y * max(negations))

        elif self.heading != 0:
            self.run(terrain)
    
    def land(self, terrain, i, translation_vector):
        chunk = terrain[i]

        #set to_ground to None
        to_ground = None
        
        # !!! this whole business might not work on vertical ledges !!!
        # add repeated checking after a collision until it collides with nothing (watch out for "just on edge" being a trigger)

        #create a vector representing the ground
        ground_edge = chunk.poly.points[1] - chunk.poly.points[0]
        # determine the sign of the slope of ground (ground will always be left to right)
        if collision.side(chunk.poly.points[1], chunk.poly.points[0], self.standing_rectangle.points[3]) > 0 and collision.side(chunk.poly.points[1], chunk.poly.points[0], self.standing_rectangle.points[2]) > 0:
            if chunk.poly.points[1].y >= chunk.poly.points[0].y:
                #if left foot within ground x
                if chunk.poly.points[0].x < self.standing_rectangle.points[0].x < chunk.poly.points[1].x:
                    #if connection to the right and position after rotate will be off ground
                    if chunk.connect_right and self.standing_rectangle.points[0].x + ground_edge.normalize().x * self.width / 2 > chunk.poly.points[1].x:
                        #keep falling - no adjustment
                        self.translate(-1 * translation_vector)
                    else:
                        #flip as normal
                        to_ground = i
                        origin = self.standing_rectangle.points[0]
                        target = math.acos(vector.Vector(1, 0).dot(ground_edge) / ground_edge.get_magnitude())
                # if right foot within ground x
                elif chunk.poly.points[0].x < self.standing_rectangle.points[1].x < chunk.poly.points[1].x:
                    #flip around left end of ground
                    origin = chunk.poly.points[0]
                    # connection to the left and position after rotate will be off ground
                    if chunk.connect_left and self.position.x < chunk.poly.points[0].x:
                        #flip onto left connect
                        to_ground = i - 1
                        connect_edge = terrain[to_ground].poly.points[1] - terrain[to_ground].poly.points[0]
                        target = math.acos(vector.Vector(1, 0).dot(connect_edge) / connect_edge.get_magnitude())
                        if terrain[to_ground].poly.points[1].y < terrain[to_ground].poly.points[0].y:
                            target = target * -1
                    else:
                        #flip onto ground
                        to_ground =  i
                        target = math.acos(vector.Vector(1, 0).dot(ground_edge) / ground_edge.get_magnitude())
            else:
                if chunk.poly.points[0].x < self.standing_rectangle.points[1].x < chunk.poly.points[1].x:
                    if chunk.connect_left and self.standing_rectangle.points[1].x - ground_edge.normalize().x * self.width / 2 < chunk.poly.points[0].x:
                        #keep falling - no adjustment
                        self.translate(-1 * translation_vector)
                    else:
                        #flip as normal
                        to_ground = i
                        origin = self.standing_rectangle.points[1]
                        target = -1 * math.acos(vector.Vector(1, 0).dot(ground_edge) / ground_edge.get_magnitude())
                elif chunk.poly.points[0].x < self.standing_rectangle.points[0].x < chunk.poly.points[1].x:
                    #flip around right end of ground
                    origin = chunk.poly.points[1]
                    if chunk.connect_right and self.position.x >= chunk.poly.points[1].x:
                        #flip onto right connect
                        to_ground = i + 1
                        connect_edge = terrain[to_ground].poly.points[1] - terrain[to_ground].poly.points[0]
                        target = math.acos(vector.Vector(1, 0).dot(connect_edge) / connect_edge.get_magnitude())
                        if terrain[to_ground].poly.points[1].y < terrain[to_ground].poly.points[0].y:
                            target = target * -1
                    else:
                        #flip onto ground
                        to_ground = i
                        target = -1 * math.acos(vector.Vector(1, 0).dot(ground_edge) / ground_edge.get_magnitude())

        # land or dont land depending on results (set rotation and grounded and zero velocity) be sure to check collision on rotate (if collision dont rotate or land)
        if to_ground is not None:
            
            ignore = [to_ground]
            if terrain[to_ground].connect_left:
                ignore.append(to_ground - 1)
            if terrain[to_ground].connect_right:
                ignore.append(to_ground + 1)

            success = self.rotate(terrain, origin, target, ignore, True) # doesnt matter if last param is true or false

            if success:
                self.grounded = to_ground
                self.velocity = vector.Vector(0, 0)
                return True
        return False

    def run(self, terrain):
        ground = terrain[self.grounded]
        ground_edge = ground.poly.points[1] - ground.poly.points[0]
        #modify velocity to correct angle
        modified_velocity = ground_edge.normalize() * self.heading * self.walking_speed

        if self.crouched:
            rectangle = self.crouched_rectangle
        else:
            rectangle = self.standing_rectangle

        if self.heading == -1:
            if ground.connect_left and self.position.x + modified_velocity.x < ground.poly.points[0].x:
                velocity_before = ground.poly.points[0] - self.position
                stop = False
                for i, chunk in enumerate(terrain):
                    if i != self.grounded and i != self.grounded - 1:
                        result = collision.grounded_collision(rectangle, chunk.poly, velocity_before) #add crouch functionality
                        if result[0]:
                            velocity_before += result[1]
                            stop = True
                
                self.translate(velocity_before)

                if not stop:
                    next_ground = terrain[self.grounded - 1]
                    next_ground_edge = next_ground.poly.points[1] - next_ground.poly.points[0]
                    target = math.acos(vector.Vector(1, 0).dot(next_ground_edge) / next_ground_edge.get_magnitude())
                    if next_ground.poly.points[1].y < next_ground.poly.points[0].y:
                        target = target * -1

                    success = self.rotate(terrain, self.position, target, (self.grounded, self.grounded - 1), False)
                
                if success:
                    self.grounded -= 1
                    velocity_after = next_ground_edge.normalize() * (modified_velocity.get_magnitude() - velocity_before.get_magnitude())
                    for i, chunk in enumerate(terrain):
                        if i > self.grounded + 1 or i < self.grounded - 1:
                            result = collision.grounded_collision(rectangle, chunk.poly, velocity_after) #add crouch functionality
                            if result[0]:
                                velocity_after += result[1]
                
                    self.translate(velocity_after)
                
            elif rectangle.points[1].x + modified_velocity.x < ground.poly.points[0].x:
                velocity_before = ground.poly.points[0] - rectangle.points[1]
                stop = False
                for i, chunk in enumerate(terrain):
                    if i != self.grounded:
                        result = collision.grounded_collision(rectangle, chunk.poly, velocity_before) #add crouch functionality
                        if result[0]:
                            velocity_before += result[1]
                            stop = True
                
                self.translate(velocity_before)

                if not stop:
                    success = self.rotate(terrain, self.standing_rectangle.points[1], 0, (self.grounded,), True)
                
                if success:
                    self.crouched = False
                    velocity_after = vector.Vector(-1 * (modified_velocity.get_magnitude() - velocity_before.get_magnitude()), 0)
                    for i, chunk in enumerate(terrain):
                        if i != self.grounded:
                            result = collision.grounded_collision(self.standing_rectangle, chunk.poly, velocity_after)
                            if result[0]:
                                velocity_after += result[1]
                
                    self.translate(velocity_after)
                    self.grounded = None
            
            else:
                for i, chunk in enumerate(terrain):
                    if not (i == self.grounded or (ground.connect_left and i == self.grounded - 1)):
                        result = collision.grounded_collision(rectangle, chunk.poly, modified_velocity)
                        if result[0]:
                            modified_velocity += result[1]
                
                self.translate(modified_velocity)
        else:
            if ground.connect_right and self.position.x + modified_velocity.x > ground.poly.points[1].x:
                velocity_before = ground.poly.points[1] - self.position
                stop = False
                for i, chunk in enumerate(terrain):
                    if i != self.grounded and i != self.grounded + 1:
                        result = collision.grounded_collision(rectangle, chunk.poly, velocity_before) #add crouch functionality
                        if result[0]:
                            velocity_before += result[1]
                            stop = True
                
                self.translate(velocity_before)

                if not stop:
                    next_ground = terrain[self.grounded + 1]
                    next_ground_edge = next_ground.poly.points[1] - next_ground.poly.points[0]
                    target = math.acos(vector.Vector(1, 0).dot(next_ground_edge) / next_ground_edge.get_magnitude())
                    if next_ground.poly.points[1].y < next_ground.poly.points[0].y:
                        target = target * -1
                    success = self.rotate(terrain, self.position, target, (self.grounded, self.grounded + 1), False)
                
                if success:
                    self.grounded += 1
                    velocity_after = next_ground_edge.normalize() * (modified_velocity.get_magnitude() - velocity_before.get_magnitude())
                    for i, chunk in enumerate(terrain):
                        if i > self.grounded + 1 or i < self.grounded - 1:
                            result = collision.grounded_collision(rectangle, chunk.poly, velocity_after) #add crouch functionality
                            if result[0]:
                                velocity_after += result[1]
                
                    self.translate(velocity_after)
                
            elif rectangle.points[0].x + modified_velocity.x > ground.poly.points[1].x:
                velocity_before = ground.poly.points[1] - rectangle.points[0]
                stop = False
                for i, chunk in enumerate(terrain):
                    if i != self.grounded:
                        result = collision.grounded_collision(rectangle, chunk.poly, velocity_before) #add crouch functionality
                        if result[0]:
                            velocity_before += result[1]
                            stop = True
                
                self.translate(velocity_before)

                if not stop:
                    success = self.rotate(terrain, self.standing_rectangle.points[0], 0, (self.grounded,), True)
                
                if not stop:
                    self.crouched = False
                    velocity_after = vector.Vector((modified_velocity.get_magnitude() - velocity_before.get_magnitude()), 0)
                    for i, chunk in enumerate(terrain):
                        if i != self.grounded:
                            result = collision.grounded_collision(self.standing_rectangle, chunk.poly, velocity_after)
                            if result[0]:
                                velocity_after += result[1]
                
                    self.translate(velocity_after)
                    self.grounded = None
            
            else:
                for i, chunk in enumerate(terrain):
                    if not (i == self.grounded or (ground.connect_right and i == self.grounded + 1)):
                        result = collision.grounded_collision(rectangle, chunk.poly, modified_velocity)
                        if result[0]:
                            modified_velocity += result[1]
                
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
    
    def jump(self, terrain):

        ground = terrain[self.grounded]

        if ground.poly.points[1].y >= ground.poly.points[0].y:
            origin = self.standing_rectangle.points[0]
        else:
            origin = self.standing_rectangle.points[1]
        
        success = self.rotate(terrain, origin, 0, (self.grounded,), True)

        if success:
            previous = self.grounded
            self.grounded = None
            self.crouched = False
            self.velocity = vector.Vector(0, -10)
            return (True, previous)
        return (False,)

        #implement some way to clear the ground on first frame
    
    def translate(self, velocity):
        self.position += velocity
        self.standing_rectangle.translate(velocity)
        self.crouched_rectangle.translate(velocity)
    
    '''
    Check if a rotation is safe from a crouched or standing state and rotate accordingly.
    Take the terrain of the stage, the origin of the rotation, the target angle, a tuple of chunks to ignore, and a boolean representing whether the rotation must be made standing.
    Rotate the soldier if able.
    Return a boolean representing the success or failure of the transformation.
    '''
    def rotate(self, terrain, origin, target, ignore, stand):
        success = True
        if self.rotation != target: #might save some operations in a few cases

            if self.crouched and not stand:
                standing = False
                rectangle = self.crouched_rectangle
                follower = self.standing_rectangle
            else:
                standing = True
                rectangle = self.standing_rectangle
                follower = self.crouched_rectangle
            
            #might make this a helper function (there are 2 occurances but i have no idea what to call the function or how to justify it)
            if target == 0: #we can have funny conditionals in here because the only case where the origin is not one of these conditions is when self.rotation = 0 (see top conditional) (but right now imma justbe safe)
                if origin.x == self.position.x and origin.y == self.position.y: #consider adding __eq__ __ne__ to vector
                    self.reset(origin, standing)
                elif origin.x == rectangle.points[0].x and origin.y == rectangle.points[0].y: #consider adding __eq__ __ne__ to vector
                    self.reset(origin + vector.Vector(self.width / 2, 0), standing)
                elif origin.x == rectangle.points[1].x and origin.y == rectangle.points[1].y: #consider adding __eq__ __ne__ to vector
                    self.reset(origin + vector.Vector(self.width / -2, 0), standing)
            else:
                rectangle.rotate(origin, target - self.rotation)

            for i, chunk in enumerate(terrain):
                if not i in ignore:
                    result = collision.grounded_collision(rectangle, chunk.poly, vector.Vector(0, 0)) #maybe this should be air? lets have a look at the collision algorithms later and optimize them a bit
                    if result[0]:
                        rectangle.rotate(origin, self.rotation - target) #add reset in here
                        success = False
                        break
            
            if success:
                if target == 0: #we can have funny conditionals in here because the only case where the origin is not one of these conditions is when self.rotation = 0 (see top conditional) (but right now imma justbe safe)
                    if origin.x == self.position.x and origin.y == self.position.y: #consider adding __eq__ __ne__ to vector
                        self.reset(origin, not standing)
                    elif origin.x == follower.points[0].x and origin.y == follower.points[0].y: #consider adding __eq__ __ne__ to vector
                        self.position = origin + vector.Vector(self.width / 2, 0)
                        self.reset(self.position, not standing)
                    elif origin.x == follower.points[1].x and origin.y == follower.points[1].y: #consider adding __eq__ __ne__ to vector
                        self.position = origin + vector.Vector(self.width / -2, 0)
                        self.reset(self.position, not standing)
                else:
                    follower.rotate(origin, target - self.rotation)
                    self.position = self.position.rotate(origin, target - self.rotation)
                
                self.rotation = target
        return success
    
    '''
    Calculate the points of the standing or crouched collision rectangle reset to a rotation of 0 based on a desired location of the players "position".
    Take a vector representing the position after the rotation and a boolean representing standing (true) or crouched (false).
    Return a rectangle after reset.
    '''
    def reset(self, position, standing):
        if standing:
            rectangle = self.standing_rectangle #works cuz implicit
            height = self.width * 2
        else:
            rectangle = self.crouched_rectangle
            height = self.width
        
        rectangle.points[0] = position + vector.Vector(self.width / -2, 0)
        rectangle.points[1] = position + vector.Vector(self.width / 2, 0)
        rectangle.points[2] = position + vector.Vector(self.width / 2, -1 * height)
        rectangle.points[3] = position + vector.Vector(self.width / -2, -1 * height)