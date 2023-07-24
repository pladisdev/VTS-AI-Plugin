import random
from modules.gui import GUI

class Vtube_Control():

    def __init__(self):
        ########################################### head variables ###########################################

        #When the random head movements should occur, is set to a random value each time
        self.head_move = 0

        #Values to set head position for vtube studio. With lerp, head movements will move towards target
        self.head = [0,0,0]
        self.target_head = [0,0,0]

        self.head_min = [0,0,0]
        self.head_max = [0,0,0]

        self.head_speed = [0,0]

        self.head_state = "Still"

        ########################################### Eye variables ###########################################

        #When the random eye movements should occur, is set to a random value each time
        self.eye_move = 0

        #Values to set head position for vtube studio. With lerp, eye movements will move towards target
        self.eyes = [0,0]
        self.target_eyes = [0,0]

        self.eyes_min = [0,0]
        self.eyes_max = [0,0]

        self.eyes_speed = [0,0]

        self.eyes_state = "Still"

        ########################################### Eye lids variables ###########################################

        #When blinking should occur, is set to a random value each time
        self.eye_lids_move = 0

        #Values to set head position for vtube studio. 1 for eyes open and 0 for close.
        self.eye_lids = [1,1]

        self.blink_range = [1,8]

        self.blink_time = 0

        self.blink_length = .1

        self.blink_state = "Open"

        self.eye_lids_state = "Blink"

    #for calculating in between points
    def lerp(self, a, b, t):
        return a + (b - a) * t

    def head_movement(self, current_time):
        #Only sets once
        if self.head_state == "Still":
            if self.head[0] + self.head[1] + self.head[2] != 0:
                self.head[0] = 0
                self.head[1] = 0
                self.head[2] = 0

        #Moves the head to a random position over time, at random intervals 
        elif self.head_state == "Random":
            if current_time > self.head_move:
                self.head_move = current_time + random.uniform(self.head_speed[0], self.head_speed[1])
                self.target_head[0] = random.uniform(self.head_min[0], self.head_max[0])
                self.target_head[1] = random.uniform(self.head_min[1], self.head_max[1])
                self.target_head[2] = random.uniform(self.head_min[2], self.head_max[2])

            self.head[0] = self.lerp(self.head[0], self.target_head[0], 0.1)
            self.head[1] = self.lerp(self.head[1], self.target_head[1], 0.1)
            self.head[2] = self.lerp(self.head[2], self.target_head[2], 0.1)
        
    def eye_movement(self, current_time):
        #Only sets once
        if self.eyes_state == "Still":
            if self.eyes[0] + self.eyes[1] != 0:
                self.eyes[0] = 0
                self.eyes[1] = 0

        #Moves the eyes to a random position over time, at random intervals 
        elif self.eyes_state == "Random":
            if current_time > self.eye_move:
                self.eye_move = current_time + random.uniform(self.eyes_speed[0], self.eyes_speed[1])
                self.target_eyes[0] = random.uniform(self.eyes_min[0], self.eyes_max[0])
                self.target_eyes[1] = random.uniform(self.eyes_min[1], self.eyes_max[1])

            self.eyes[0] = self.lerp(self.eyes[0], self.target_eyes[0], .5)
            self.eyes[1] = self.lerp(self.eyes[1], self.target_eyes[1], .5)

    def eye_lid_movement(self, current_time):

        if self.eye_lids_state == "Blink":
            if current_time > self.blink_time and self.blink_state == "Blink":
                self.blink_time = current_time + random.uniform(self.blink_range[0], self.blink_range[1])
                self.eye_lids = [1,1]   
                self.blink_state = "Open"
            elif current_time > self.blink_time:
                self.blink_time = current_time + self.blink_length
                self.eye_lids = [0,0]
                self.blink_state = "Blink"
        elif self.eye_lids_state == "Open":
            self.eye_lids = [1,1]  
        elif self.eye_lids_state == "Close":
            self.eye_lids = [0,0]   
        elif self.eye_lids_state == "Wink":
            if self.blink_state == "Wink" and current_time > self.blink_time:
                self.blink_state = "Blink"
                self.eye_lids_state = "Blink"
            elif self.blink_state != "Wink":
                self.blink_time = current_time + self.blink_length*5      
                if bool(random.getrandbits(1)):
                    self.eye_lids = [0,1]
                else:
                    self.eye_lids = [1,0]

                self.blink_state = "Wink"
    
    def gui_update(self, gui : GUI):
        #Gets updated vars from GUI when a value changes
        self.head_state = gui.head_state
        self.head_speed[0] = gui.head_target_speed_min*5
        self.head_speed[1] = gui.head_target_speed_max*5

        if self.head_speed[0] > self.head_speed[1]:
            self.head_speed[0] = self.head_speed[1]
        elif self.head_speed[1] < self.head_speed[0]:
            self.head_speed[1] = self.head_speed[0]

        self.head_min[0] = (1-gui.head_x_min)*-30
        self.head_max[0] = gui.head_x_max*30
        self.head_min[1] = (1-gui.head_y_min)*-30
        self.head_max[1] = gui.head_y_max*30
        self.head_min[2] = (1-gui.head_z_min)*-90
        self.head_max[2] = gui.head_z_max*90

        self.eyes_state = gui.eyes_state
        self.eyes_speed[0] = gui.eyes_target_speed_min*5
        self.eyes_speed[1] = gui.eyes_target_speed_max*5

        if self.eyes_speed[0] > self.eyes_speed[1]:
            self.eyes_speed[0] = self.eyes_speed[1]
        elif self.eyes_speed[1] < self.eyes_speed[0]:
            self.eyes_speed[1] = self.eyes_speed[0]

        self.eyes_min[0] = (1-gui.eyes_x_min)*-1
        self.eyes_max[0] = gui.eyes_x_max
        self.eyes_min[1] = (1-gui.eyes_y_min)*-1
        self.eyes_max[1] = gui.eyes_y_max

        self.eye_lids_state = gui.eye_lids