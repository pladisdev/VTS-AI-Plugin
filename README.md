# VTS-AI-Plugin
 An async plugin for Vtube Studio to control model with python. For AI vtubers.
 
## Explanation
### What is it?
This is a simple python example to remotely control a vtuber model using Vtube Studio's API. You can currently:
* Set random head movements
* Set random eye movements
* Set and toggle expressions
* Video demonstration: https://www.youtube.com/watch?v=zEsLiZGpNhA

### Why is this useful? 
* For AI vtubers, vtuber models need to controlled via code. This is an example to control a model via code, allowing you to toggle expressions based on AI inputs, like mood or prompts. 
* This is also an example of having random eye and head movements, which can give a more natural feeling than looping animations (or no animations). 

## Instructions
* Follow the instructions here in creating a plugin for VTS: https://github.com/DenchiSoft/VTubeStudio/wiki/Plugins
More info can be found here: https://github.com/DenchiSoft/VTubeStudio/

* You only need 'pip install aioconsole' to run main.py
* Add your plugin information in the script. Your plugin name, developer name, and token
* Then just run it your favorite way, ie python main.py

## TODO
* This is just an example plugin, but I believe it can be improved to be more generailized. Perhaps there should be an async and non async version.
* Use an actual neural network to have more natural speaking animations. The input for the neural network would be voice, with outputs being x,y, and z values for head movement as well as x and y for eye movements. Additonal paramters could also be outputs. Training data could be collected with real vtubers.




