# VTS-AI-Plugin
 An async plugin for Vtube Studio to control model with python. For AI vtubers.
 
## Explanation
### What is it?
This is a simple python example to remotely control a vtuber model using Vtube Studio's API. You can currently:
* Set random head movements
* Set random eye movements
* Blinking
* Set and toggle expressions
* Video demonstration: https://www.youtube.com/watch?v=rbA7PNE8CoE

### Why is this useful? 
* For AI vtubers, vtuber models need to controlled via code. This is an example to control a model via code, allowing you to toggle expressions based on AI inputs, like mood or prompts. 
* This is also an example of having random eye and head movements, which can give a more natural feeling than looping animations (or no animations). 

## Instructions
* You only need ```pip install aioconsole``` to run main.py and ```pip install websockets``` to run vts.py
* Have Vtube Studio open, and in VTS settings, enable Start  API (allow plugins)
* Then just run it your favorite way, ie ```python main.py```
* When a pop-up appears, select Allow
* Currently, the API injects parameters values for ```FaceAngleX, FaceAngleY, FaceAngleZ, EyeLeftX, and EyeLeftY``` for the parameters for your vtubers models that control face and eye movements. These are default and should already be set, but make sure in the model settings that they are. For some reason using these values cause the Vtube Studio watermark to appear, even when paid. I believe the solution is switching to custom parameters (I think Vtube Studio expects these values to come from a phone app, which also needs to be paid for).
* You should adjust these values so they appear natural for random movements, for your vtuber model.
* You can create different expressions which can then be toggled by the script.


## TODO
* This is just an example plugin, but I believe it can be improved to be more generailized. Perhaps there should be an async and non async version.
* Use an actual neural network to have more natural speaking animations. The input for the neural network would be voice, with outputs being x,y, and z values for head movement as well as x and y for eye movements. Additonal paramters could also be outputs. Training data could be collected with real vtubers.




