import asyncio
import random
import time

#pip install aioconsole
from aioconsole import ainput

from vts import VTS_API

#Make sure to create a Vtube Studio plugin first
URL = "ws://localhost:8001/" #Verify this is the right port
PLUGIN_NAME = "Enter your plugin name here" #Name should match custom plugin in vtube studio
DEVELOPER_NAME = "Enter your developer name here" #Should match as well
TOKEN = "enter your plugin token here" #"insert vtube studio token here"

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
    vtube_studio = VTS_API(URL, PLUGIN_NAME, DEVELOPER_NAME, TOKEN, queue)

    ########################################### head variables ###########################################

    #sets the movement of the head to be still
    head_movement = "still"

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

    #sets the eye movement to stare forwards
    eye_movement = "stare"
    
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

    #Sets eye and head movement to 0
    await queue.put({"state" : "head movement", "val" : {"x" : head_x, "y" : head_y,  "z" : head_z}})
    await queue.put({"state" : "eye movement", "val" : {"x" : eye_x, "y" : eye_y}})

    #Creates task for user input, is async and non-blocking
    user_queue = asyncio.Queue()
    user_input_task = asyncio.create_task(get_user_input(user_queue))

    while True:
        
        #Wait to not abuse CPU, and should be greater than VTS so the queue doesn't pile up
        await asyncio.sleep(.1)

        if queue.qsize() > 20:
            print("warning: queue is growing to much")

        current_time = time.time()

        #For user input
        if not user_queue.empty():
            input_from_user = await user_queue.get()
            if input_from_user == "stop":
                break
            elif input_from_user == "hs":
                head_movement = "still"
            elif input_from_user == "hr":
                head_movement = "random"
            elif input_from_user == "es":
                eye_movement = "stare"
            elif input_from_user == "er":
                eye_movement = "random"
            else: #For settings expressions
                await queue.put({"state" : "toggle expression", "expression" : input_from_user})

        #Only sets once
        if head_movement == "still":
            if head_x + head_y + head_z != 0:
                head_x = 0
                head_y = 0
                head_z = 0
                await queue.put({"state" : "head movement", "val" : {"x" : head_x, "y" : head_y,  "z" : head_z}})

        #Moves the head to a random position over time, at random intervals 
        elif head_movement == "random":
            if current_time > head_move:
                head_move = current_time + random.uniform(1, 5)
                target_head_x = random.uniform(-30, 30)
                target_head_y = random.uniform(-30, 30)
                target_head_z = random.uniform(-90, 90)

            head_x = lerp(head_x, target_head_x, 0.1)
            head_y = lerp(head_y, target_head_y, 0.1)
            head_z = lerp(head_z, target_head_z, 0.1)
            await queue.put({"state" : "head movement", "val" : {"x" : head_x, "y" : head_y,  "z" : head_z}})

        #Only sets once
        if eye_movement == "stare":
            if eye_x + eye_y != 0:
                eye_x = 0
                eye_y = 0
                await queue.put({"state" : "eye movement", "val" : {"x" : eye_x, "y" : eye_y}})

        #Moves the eyes to a random position over time, at random intervals 
        elif eye_movement == "random":
            if current_time > eye_move:
                eye_move = current_time + random.uniform(1, 6)
                target_eye_x = random.uniform(-1.0, 1.0)
                target_eye_y = random.uniform(-1.0, 1.0)

            eye_x = lerp(eye_x, target_eye_x, .5)
            eye_y = lerp(eye_y, target_eye_y, .5)
            await queue.put({"state" : "eye movement", "val" : {"x" : eye_x, "y" : eye_y}})

    #For a clean exit (could be cleaner)
    await vtube_studio.end()
    user_input_task.cancel()

if(__name__ == '__main__'):
    asyncio.run(main())
