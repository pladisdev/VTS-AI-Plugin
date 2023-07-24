import asyncio
import time

from vtube_studio.vts import VTS_API
from modules.gui import GUI
from modules.vtuber_movement import Vtube_Control

#Make sure to create a Vtube Studio plugin first
URL = "ws://localhost:8001/" #Verify this is the right port

async def main():

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

        # load GUI with expression found in vtube studio
        gui = GUI(expressions)

        #Sets eye and head movement to 0
        await vtube_studio.ai_movement(movement.head, movement.eyes, movement.eye_lids)

        expression = ""

        #Main loop
        while True:
            
            if gui.exit:
                break
            elif gui.new_expression:
                expression = gui.expression
                await vtube_studio.toggle_expression(expression)
                gui.new_expression = False
            elif gui.value_change: 
                movement.gui_update(gui)
                gui.value_change = False

            current_time = time.time()

            movement.head_movement(current_time)
            movement.eye_movement(current_time)
            movement.eye_lid_movement(current_time)

            await vtube_studio.ai_movement(movement.head, movement.eyes, movement.eye_lids)
          
            #Frame rate of controlling vtube studio, set to 10 FPS
            await asyncio.sleep(.1)

    await gui.end()

if(__name__ == '__main__'):
    asyncio.run(main())