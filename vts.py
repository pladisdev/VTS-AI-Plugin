import json
import asyncio
import base64
import configparser

import websockets

#For storing expression for your model, can become more complex over times
class Expression:
    def __init__(self, name, val=False):
        self.name = name
        self.val = val
    
    def toggle(self):
        self.val = not self.val
        return self.val

class VTS_API:

    model_params = [
            "FacePositionX", 
            "FacePositionY", 
            "FacePositionZ", 
            "FaceAngleX", 
            "FaceAngleY", 
            "FaceAngleZ" , 
            "MouthSmile", 
            "MouthOpen", 
            "Brows", 
            "BrowLeftY", 
            "BrowRightY", 
            "EyeOpenLeft", 
            "EyeOpenRight", 
            "EyeLeftX", 
            "EyeLeftY", 
            "EyeRightX", 
            "EyeRightY", 
        ]
    
    def __init__(self, url):
        self.url =  url

        self.ws = None

        self.expressions = []

        with open("custom_params.json") as params_file:
            self.custom_params = json.load(params_file)["custom_params"]

    async def return_expressions(self):
        names = []
        if self.expressions != []:
            names = [expression.name for expression in self.expressions]
        return names

    #Gets plugin information for authetifcation from config file
    async def load_plugin_information(self):

        DEFUALT_NAME = "VTS-AI"
        DEFAULT_DEVELOPER = "Pladis"

        PLUGIN_SETTINGS = "Plugin Settings"
        PLUGIN_NAME = "Name"
        PLUGIN_DEVELOPER = "Developer"
        PLUGIN_TOKEN = "Token"

        config = configparser.ConfigParser()
        
        try:
            files_read = config.read("config.ini")

            if not files_read:
                with open("config.ini", "w") as config_file:
                    
                    config.add_section(PLUGIN_SETTINGS)
                    config.set(PLUGIN_SETTINGS, PLUGIN_NAME, DEFUALT_NAME)
                    config.set(PLUGIN_SETTINGS, PLUGIN_DEVELOPER, DEFAULT_DEVELOPER)
                    config.set(PLUGIN_SETTINGS, PLUGIN_TOKEN, "")
                    config.write(config_file)

                return self.load_plugin_information()
        except Exception as e:
            raise e

        if not config.has_section(PLUGIN_SETTINGS):
            config.add_section(PLUGIN_SETTINGS)

        if config.has_option(PLUGIN_SETTINGS, PLUGIN_NAME):
            name = config.get(PLUGIN_SETTINGS, PLUGIN_NAME)
        else:
            config.set(PLUGIN_SETTINGS, PLUGIN_NAME, DEFUALT_NAME)
            name = DEFUALT_NAME

        if config.has_option(PLUGIN_SETTINGS, PLUGIN_DEVELOPER):
            developer = config.get(PLUGIN_SETTINGS, PLUGIN_DEVELOPER)
        else:
            config.set(PLUGIN_SETTINGS, PLUGIN_DEVELOPER, DEFAULT_DEVELOPER)
            developer = DEFAULT_DEVELOPER

        if config.has_option(PLUGIN_SETTINGS, PLUGIN_TOKEN):
            token = config.get(PLUGIN_SETTINGS, PLUGIN_TOKEN)
        else:
            config.set(PLUGIN_SETTINGS, PLUGIN_TOKEN, "None")
            token = ""

        if token == "" or token.lower() == "nan" or token.lower() == "none":
            token = await self.token_request(name, developer)
            config.set(PLUGIN_SETTINGS, PLUGIN_TOKEN, token)
            with open("config.ini", "w") as config_file:
                config.write(config_file)

        if token is None:
            raise "Could not get token"

        return name, developer, token

    #Main function to send message to vtube studio
    #TODO better error handling
    async def send_message(self, message_data, error=False):
        message_json = json.dumps(message_data)

        try:
            await self.ws.send(message_json)
            response = await self.ws.recv()
        except Exception as e:          
            print(f"Error sending message to Vtube Studio: {e}")
            raise e

        return json.loads(response)
    
    async def token_request(self, name, developer):
        
        try:
            with open("vts_ai_logo.png", "rb") as image_file:
                image_data = image_file.read()

            # Encode the image data to base64
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            data = {
            "pluginName": name,
            "pluginDeveloper": developer,
            "pluginIcon": image_base64
            }

        except Exception as e:
            print(e)
            data = {
            "pluginName": name,
            "pluginDeveloper": developer
            }

        token_request = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "TokenRequest",
        "messageType": "AuthenticationTokenRequest",
        "data": data
        }

        response = await self.send_message(token_request)

        if "errorID" in response["data"]:
            print("Error getting token, did you deny access in Vtube Studio? Is it open?")
        elif "authenticationToken" in response["data"]:
            return response["data"]["authenticationToken"]

        return None
        
    #Required at least once per session
    async def authenticate(self, name, developer, token):

        auth_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "Authenticate",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": name,
                "pluginDeveloper": developer,
                "authenticationToken": token
            }
        }

        await self.send_message(auth_request)

    async def get_parameters(self):
        message_data = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "InputParameterListRequest"
        }
        response = await self.send_message(message_data)
        params = []
        for param in response["data"]["defaultParameters"]:
            range = param["max"] - param["min"]
            params.append([param["name"], (param["value"] - param["min"])/range , param["min"], param["max"], range])

        return params

    async def set_custom_parameters(self):
        for data in self.custom_params:

            message_data = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "ParameterCreation",
            "messageType": "ParameterCreationRequest",
            "data": data
            }

            await self.send_message(message_data)

    async def get_expressions(self):
        message_data = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "GetExpressions",
            "messageType": "ExpressionStateRequest",
            "data": {
                "details": True,
            }
        }

        response = await self.send_message(message_data)
        
        expressions = []
        for expression_found in response["data"]["expressions"]:
            expression = Expression(expression_found["name"], expression_found["active"])
            expressions.append(expression)

        return expressions

    async def set_expression_vts(self, expression, val):

        message_data = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SetExpression",
            "messageType": "ExpressionActivationRequest",
            "data": {
                "expressionFile": expression + ".exp3.json",
                "active": val
            }
        }

        try:
            response = await self.send_message(message_data)

            if not "data" in response:
                raise "Error in response"
        except Exception as e:
            print(f"Error setting expression: {e}")
            raise e
        
    async def set_parameters(self, params):
        message_data = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SetParameters",
            "messageType": "InjectParameterDataRequest",
            "data": {
                "mode": "set",
                "parameterValues": params
            }
        }

        return await self.send_message(message_data)
        
    async def ai_movement(self, head, eye, eye_lids):
        params =  [
                    {"id": "AIFaceAngleX", "value": head[0]},
                    {"id": "AIFaceAngleY", "value": head[1]},
                    {"id": "AIFaceAngleZ", "value": head[2]},
                    {"id": "AIEyeLeftX", "value": eye[0]},
                    {"id": "AIEyeLeftY", "value": eye[1]},
                    {"id": "AIEyeOpenLeft", "value": eye_lids[0]},
                    {"id": "AIEyeOpenRight", "value": eye_lids[1]}        
                ]
        
        await self.set_parameters(params)

    async def full_ai_movement(self, ai_params, params_config):  
        params = []

        print(ai_params)
        for config_param in params_config:
            for model_param, ai_param in zip(self.model_params, ai_params):
                if model_param == config_param[0]:
                    params.append({"id": config_param[0], "value": (ai_param * config_param[4]) + config_param[2] })
                    break
        
        await self.set_parameters(params)
    
    async def __aenter__(self):

        self.ws = await websockets.connect(self.url)
        name, developer, token = await self.load_plugin_information()
        await self.authenticate(name, developer, token)
        self.expressions = await self.get_expressions()

        for expression in self.expressions:
            if expression.val:
                await self.set_expression(expression.name, expression.toggle())

        await self.set_custom_parameters()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.ws:
            await self.ws.close()

    async def toggle_expression(self, name):

        expression = [expression for expression in self.expressions if expression.name == name]

        if expression != []:
            await self.set_expression_vts(expression[0].name, expression[0].toggle())

    async def set_expression(self, name, value):
        expression = [expression for expression in self.expressions if expression.name == name]

        if expression != []:
            if value != expression[0].val:
                await self.set_expression_vts(expression[0].name, expression[0].toggle())

    async def vtuber_movement(self, head, eyes, eye_lids):          
            await self.set_parameters(head, eyes, eye_lids)
