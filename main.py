import asyncio
import random
import time

#pip install aioconsole
from aioconsole import ainput

from vts import VTS_API
from gui import GUI

#Make sure to create a Vtube Studio plugin first
URL = "ws://localhost:8001/" #Verify this is the right port

#for calculating in between points
def lerp(a, b, t):
    return a + (b - a) * t

#async user input, works for windows at least
async def get_user_input(user_queue):
    user_input = ""
    while user_input != "stop":
        user_input = await ainput("Enter 'hs' to stop head movement, 'hr' for random head movement. Enter 'es' to stop eye movement, 'er' for random eye movement. Enter expression name to toggle expression. Enter 'stop' to stop: ")
        await user_queue.put(user_input)

async def main():

    ########################################### Vtube Studio settings ###########################################

    queue = asyncio.Queue()
    vtube_studio = VTS_API(URL, queue)

    ########################################### head variables ###########################################

    #When the random head movements should occur, is set to a random value each time
    head_move = 0

    #Values to set head position for vtube studio. With lerp, head movements will move towards target
    head_x = 0
    head_y = 0
    head_z = 0
    target_head_x = 0
    target_head_y = 0
    target_head_z = 0  

    ########################################### Eye variables ###########################################

    #When the random eye movements should occur, is set to a random value each time
    eye_move = 0

    #Values to set head position for vtube studio. With lerp, head movements will move towards target
    eye_x = 0
    eye_y = 0
    target_eye_x = 0
    target_eye_y = 0
    
    ########################################### Model Expressions ###########################################

    #Wait for connection to vtube studio and get expressions
    #TODO probably should have a flag to wait till vtube is connected, and expressions are set

    while not vtube_studio.authenticate_flag:
        await asyncio.sleep(.1)

    expressions = None
    timeout = time.time()+10
    while expressions is None and time.time() < timeout:
        await asyncio.sleep(.1)
        expressions = await vtube_studio.return_expressions()
    
    #Throw error if no expressions found, usually means vtube studio did not connect properly
    if expressions is None:
        print("No expressions found")
        raise "No expressions found"
    
    print(f"Expressions in model: {expressions}")

    gui = GUI(expressions)

    #Sets eye and head movement to 0
    await queue.put({"state" : "head movement", "val" : {"x" : head_x, "y" : head_y,  "z" : head_z}})
    await queue.put({"state" : "eye movement", "val" : {"x" : eye_x, "y" : eye_y}})

    expression = ""

    while True:
        
        #Wait to not abuse CPU, and should be greater than VTS so the queue doesn't pile up
        await asyncio.sleep(.1)

        #Gets updated vars from GUI when a value changes
        if gui.exit:
            break
        elif gui.value_change:

            if gui.expression != expression:
                expression = gui.expression
                await queue.put({"state" : "toggle expression", "expression" : expression})

            head_state = gui.head_state
            head_target_speed_min = gui.head_target_speed_min*5
            head_target_speed_max = gui.head_target_speed_max*5

            if head_target_speed_min > head_target_speed_max:
                head_target_speed_min = head_target_speed_max
            elif head_target_speed_max < head_target_speed_min:
                head_target_speed_max = head_target_speed_min

            head_x_min = (1-gui.head_x_min)*-30
            head_x_max = gui.head_x_max*30
            head_y_min = (1-gui.head_y_min)*-30
            head_y_max = gui.head_y_max*30
            head_z_min = (1-gui.head_z_min)*-90
            head_z_max = gui.head_z_max*90

            eyes_state = gui.eyes_state
            eyes_target_speed_min = gui.eyes_target_speed_min*5
            eyes_target_speed_max = gui.eyes_target_speed_max*5

            if eyes_target_speed_min > eyes_target_speed_max:
                eyes_target_speed_min = eyes_target_speed_max
            elif eyes_target_speed_max < eyes_target_speed_min:
                eyes_target_speed_max = eyes_target_speed_min

            eyes_x_min = (1-gui.eyes_x_min)*-1
            eyes_x_max = gui.eyes_x_max
            eyes_y_min = (1-gui.eyes_y_min)*-1
            eyes_y_max = gui.eyes_y_max

            gui.value_change = False

        if queue.qsize() > 20:
            gui.update_error("warning: queue is growing to much")

        current_time = time.time()

        #Only sets once
        if head_state == "Still":
            if head_x + head_y + head_z != 0:
                head_x = 0
                head_y = 0
                head_z = 0
                await queue.put({"state" : "head movement", "val" : {"x" : head_x, "y" : head_y,  "z" : head_z}})

        #Moves the head to a random position over time, at random intervals 
        elif head_state == "Random":
            if current_time > head_move:
                head_move = current_time + random.uniform(head_target_speed_min, head_target_speed_max)
                target_head_x = random.uniform(head_x_min, head_x_max)
                target_head_y = random.uniform(head_y_min, head_y_max)
                target_head_z = random.uniform(head_z_min, head_z_max)

            head_x = lerp(head_x, target_head_x, 0.1)
            head_y = lerp(head_y, target_head_y, 0.1)
            head_z = lerp(head_z, target_head_z, 0.1)
            await queue.put({"state" : "head movement", "val" : {"x" : head_x, "y" : head_y,  "z" : head_z}})

        #Only sets once
        if eyes_state == "Still":
            if eye_x + eye_y != 0:
                eye_x = 0
                eye_y = 0
                await queue.put({"state" : "eye movement", "val" : {"x" : eye_x, "y" : eye_y}})

        #Moves the eyes to a random position over time, at random intervals 
        elif eyes_state == "Random":
            if current_time > eye_move:
                eye_move = current_time + random.uniform(eyes_target_speed_min, eyes_target_speed_max)
                target_eye_x = random.uniform(eyes_x_min, eyes_x_max)
                target_eye_y = random.uniform(eyes_y_min, eyes_y_max)

            eye_x = lerp(eye_x, target_eye_x, .5)
            eye_y = lerp(eye_y, target_eye_y, .5)
            await queue.put({"state" : "eye movement", "val" : {"x" : eye_x, "y" : eye_y}})

    #For a clean exit (could be cleaner)
    await gui.end()
    await vtube_studio.end()

if(__name__ == '__main__'):
    asyncio.run(main())
