import asyncio
import random
import time

from vts import VTS_API
from gui import GUI

#Make sure to create a Vtube Studio plugin first
URL = "ws://localhost:8001/" #Verify this is the right port

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

        if current_time > self.blink_time and self.blink_state == "Blink":
            self.blink_time = current_time + random.uniform(self.blink_range[0], self.blink_range[1])
            self.eye_lids = [1,1]   
            self.blink_state = "Open"
        elif current_time > self.blink_time:
            self.blink_time = current_time + self.blink_length
            self.eye_lids = [0,0]
            self.blink_state = "Blink"

async def main():


    ########################################### Vtube Studio settings ###########################################

    movement = Vtube_Control()

    async with VTS_API(URL) as vtube_studio:
 
    ########################################### Model Expressions ###########################################

        #Wait for connection to vtube studio and get expressions
        #TODO probably should have a flag to wait till vtube is connected, and expressions are set

        expressions = []
        timeout = time.time()+10
        while expressions == [] and time.time() < timeout:
            await asyncio.sleep(.1)
            expressions = await vtube_studio.return_expressions()
        
        print(f"Expressions in model: {expressions}")

        gui = GUI(expressions)

        #Sets eye and head movement to 0
        await vtube_studio.ai_movement(movement.head, movement.eyes, movement.eye_lids)

        expression = ""

        while True:
            #Gets updated vars from GUI when a value changes
            if gui.exit:
                break
            elif gui.value_change:

                if gui.expression != expression:
                    expression = gui.expression
                    await vtube_studio.toggle_expression(expression)

                movement.head_state = gui.head_state
                movement.head_speed[0] = gui.head_target_speed_min*5
                movement.head_speed[1] = gui.head_target_speed_max*5

                if movement.head_speed[0] > movement.head_speed[1]:
                    movement.head_speed[0] = movement.head_speed[1]
                elif movement.head_speed[1] < movement.head_speed[0]:
                    movement.head_speed[1] = movement.head_speed[0]

                movement.head_min[0] = (1-gui.head_x_min)*-30
                movement.head_max[0] = gui.head_x_max*30
                movement.head_min[1] = (1-gui.head_y_min)*-30
                movement.head_max[1] = gui.head_y_max*30
                movement.head_min[2] = (1-gui.head_z_min)*-90
                movement.head_max[2] = gui.head_z_max*90

                movement.eyes_state = gui.eyes_state
                movement.eyes_speed[0] = gui.eyes_target_speed_min*5
                movement.eyes_speed[1] = gui.eyes_target_speed_max*5

                if movement.eyes_speed[0] > movement.eyes_speed[1]:
                    movement.eyes_speed[0] = movement.eyes_speed[1]
                elif movement.eyes_speed[1] < movement.eyes_speed[0]:
                    movement.eyes_speed[1] = movement.eyes_speed[0]

                movement.eyes_min[0] = (1-gui.eyes_x_min)*-1
                movement.eyes_max[0] = gui.eyes_x_max
                movement.eyes_min[1] = (1-gui.eyes_y_min)*-1
                movement.eyes_max[1] = gui.eyes_y_max

                gui.value_change = False

            ###################################### Main logic for vtuber movement ######################################

            current_time = time.time()

            movement.head_movement(current_time)
            movement.eye_movement(current_time)
            movement.eye_lid_movement(current_time)

            await vtube_studio.ai_movement(movement.head, movement.eyes, movement.eye_lids)
          
            #Wait to not abuse CPU, and should be greater than VTS so the queue doesn't pile up
            await asyncio.sleep(.1)

    await gui.end()

if(__name__ == '__main__'):
    asyncio.run(main())
