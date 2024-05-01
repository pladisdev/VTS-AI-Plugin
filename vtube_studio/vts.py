import json, base64, configparser, websockets, logging, time
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

        # Create a logger instance
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Create a console handler and set the log level to be printed to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create a formatter for the log messages
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add the console handler to the logger
        self.logger.addHandler(console_handler)

        with open("vtube_studio/custom_params.json") as params_file:
            self.custom_params = json.load(params_file)["custom_params"]

    async def __aenter__(self):
        self.ws = None
        while self.ws is None:
            try:
                self.ws = await websockets.connect(self.url)
            except:
                print("Unable to connect to VTS, trying again in 3 seconds")
                time.sleep(3)
                pass
        print("VTS found")

        name, developer, token = await self.__load_plugin_information()
        await self.__authenticate(name, developer, token)
        self.expressions = await self.__get_expressions()

        for expression in self.expressions:
            if expression.val:
                await self.set_expression(expression.name, expression.toggle())

        await self.__set_custom_parameters()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.ws:
            await self.ws.close()

    #Gets plugin information for authetifcation from config file
    async def __load_plugin_information(self):

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
                self.logger.info("Creating config file")
                with open("config.ini", "w") as config_file:
                    
                    config.add_section(PLUGIN_SETTINGS)
                    config.set(PLUGIN_SETTINGS, PLUGIN_NAME, DEFUALT_NAME)
                    config.set(PLUGIN_SETTINGS, PLUGIN_DEVELOPER, DEFAULT_DEVELOPER)
                    config.set(PLUGIN_SETTINGS, PLUGIN_TOKEN, "")
                    config.write(config_file)

                return self.__load_plugin_information()
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
            self.logger.info("No token found, Allow the plugin in Vtube Studio")
            token = await self.__token_request(name, developer)
            config.set(PLUGIN_SETTINGS, PLUGIN_TOKEN, token)
            with open("config.ini", "w") as config_file:
                config.write(config_file)

        if token is None:
            raise "Could not get token"

        return name, developer, token

    #Main function to send message to vtube studio
    #TODO better error handling
    async def __send_message(self, message_data, error=False):
        message_json = json.dumps(message_data)

        try:
            await self.ws.send(message_json)
            response = await self.ws.recv()
        except Exception as e:          
            self.logger.error(str(e))
            raise e

        return json.loads(response)
    
    async def __token_request(self, name, developer):
        
        try:
            with open("vtube_studio/vts_ai_logo.png", "rb") as image_file:
                image_data = image_file.read()

            # Encode the image data to base64
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            data = {
            "pluginName": name,
            "pluginDeveloper": developer,
            "pluginIcon": image_base64
            }

        except Exception as e:
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

        response = await self.__send_message(token_request)

        if "errorID" in response["data"]:
            self.logger.error(response["message"])
            self.logger.error("Did not recieve token, did you deny access in Vtube Studio? Is it open?")
        elif "authenticationToken" in response["data"]:
            self.logger.info("Authentification Successful")
            return response["data"]["authenticationToken"]

        return None
        
    #Required at least once per session
    async def __authenticate(self, name, developer, token):

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

        await self.__send_message(auth_request)

    async def __set_custom_parameters(self):
        for data in self.custom_params:

            message_data = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "ParameterCreation",
            "messageType": "ParameterCreationRequest",
            "data": data
            }

            await self.__send_message(message_data)

    async def __get_expressions(self):
        message_data = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "GetExpressions",
            "messageType": "ExpressionStateRequest",
            "data": {
                "details": True,
            }
        }

        response = await self.__send_message(message_data)
        expressions = []
        if "errorID" in response["data"]:
            self.logger.error(response["data"]["message"])
        else:
            try:   
                for expression_found in response["data"]["expressions"]:
                    expression = Expression(expression_found["name"], expression_found["active"])
                    expressions.append(expression)
            except Exception as e:
                self.logger.error(str(e))
                self.logger.error("Response: " + str(response))

        return expressions

    async def __set_expression(self, expression, val):

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
            response = await self.__send_message(message_data)

            if "errorID" in response["data"]:
                self.logger.error(response["data"]["message"])
                
        except Exception as e:
            self.logger.error(str(e))
            raise e
        
    async def __set_parameters(self, params):
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

        return await self.__send_message(message_data)
        
    async def get_parameters(self):
        message_data = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "InputParameterListRequest"
        }
        response = await self.__send_message(message_data)
        params = []
        for param in response["data"]["defaultParameters"]:
            range = param["max"] - param["min"]
            params.append([param["name"], (param["value"] - param["min"])/range , param["min"], param["max"], range])

        return params
    
    async def return_expressions(self):
        names = []
        if self.expressions != []:
            names = [expression.name for expression in self.expressions]
        return names

    async def toggle_expression(self, name):

        expression = [expression for expression in self.expressions if expression.name == name]

        if expression != []:
            await self.__set_expression(expression[0].name, expression[0].toggle())

    async def set_expression(self, name, value):
        expression = [expression for expression in self.expressions if expression.name == name]

        if expression != []:
            if value != expression[0].val:
                await self.__set_expression(expression[0].name, expression[0].toggle())
    
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
        
        await self.__set_parameters(params)

    async def nn_movement(self, ai_params, params_config):  
        params = []
        for config_param in params_config:
            for model_param, ai_param in zip(self.model_params, ai_params):
                if model_param == config_param[0]:
                    params.append({"id": config_param[0], "value": (ai_param * config_param[4]) + config_param[2] })
                    break
        
        await self.__set_parameters(params)