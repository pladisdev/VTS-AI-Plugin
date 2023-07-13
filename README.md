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
* Control with an actual Neural Network (In ALPHA)

### Why is this useful? 
* For AI vtubers, vtuber models need to controlled via code. This is an example to control a model via code, allowing you to toggle expressions based on AI inputs, like mood or prompts. 
* This is also an example of having random eye and head movements, which can give a more natural feeling than looping animations (or no animations). 

## Instructions
### For simple Vtube Studio control with GUI
* You only need ```pip install aioconsole``` to run main.py and ```pip install websockets``` to run vts.py
* Have Vtube Studio open, and in VTS settings, enable Start  API (allow plugins)
* Then just run it your favorite way, ie ```python main.py```
* When a pop-up appears, select Allow
* Currently, the API injects parameters values for ```AIFaceAngleX, AIFaceAngleY, AIFaceAngleZ, AIEyeLeftX, AIEyeLeftY, AIEyeOpenLeft, and AIEyeOpenRight``` for the parameters for your vtubers models that control face and eye movements. These are default and should already be set, but make sure in the model settings that they are.
* You should adjust these values so they appear natural for random movements, for your vtuber model.
* You can create different expressions which can then be toggled by the script.
* You can control mouth movements with volume and frequency of audio output connected to TTS of your AI.
### For Neural Network control (In ALPHA)
* You'll need to install torch for your PC. I tested with cuda 11.8. https://pytorch.org/get-started/locally/
* ```websockets, numpy, scipy, keyboard``` are needed.
* Run ```collect_data_for_training.py``` to get values from VTS in the form of a txt file and wav file. specify your mic, and make sure your mic supports 48000 sample rate. Data is stored in ram so make sure you don't overflow by running the application for too long.
* Proper data should be you speaking normally while using a vtuber model in VTS with the plugin connected.
* Run ```vts_model_training.py``` to train the model based on data collected from the previous script.
* Run ```vts_model_inference.py``` to have a Neural Network control the vtuber movements in VTS based on voice input. An example .pth model is included but results are very much in ALPHA.

## TODO
* Improve data collection logic for VTS and Audio Input
* Improve Neural Network architechture
* Collect data based on face tracking instead of VTS parameters.
* This is just an example plugin, but I believe it can be improved to be more generailized. Perhaps there should be an async and non async version.
* A lot more




