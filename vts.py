import json
import websockets
import time
import asyncio

#For storing expression for your model, can become more complex over times
class Expression:
    def __init__(self, name, val=False):
        self.name = name
        self.val = val
    
    def toggle(self):
        self.val = not self.val
        return self.val

class VTS_API:
    def __init__(self, url, name, developer, token, queue):
        self.url =  url
        self.name = name
        self.developer = developer
        self.token = token
        self.queue = queue

        self.ws = None

        self.expressions = None

        #task runs async to main
        self.task = asyncio.create_task(self.vts(self.queue))

    #to cleanly end task and queue
    async def end(self):
        await self.queue.put(None)   
        await asyncio.sleep(.1)
        self.task.cancel()
        await asyncio.gather(*self.task, return_exceptions=True)

    async def return_expressions(self):
        names = None
        if self.expressions is not None:
            names = [expression.name for expression in self.expressions]
        return names

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
    
    #Required at least once per session
    async def authenticate(self):

        auth_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": self.name,
                "pluginDeveloper": self.developer,
                "authenticationToken": self.token
            }
        }

        await self.send_message(auth_request)

    #Function called when there is no activity happening with Vtube Studio
    #Vtube studio will disconnect otherwise
    async def pingpong(self):
        message_data = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "MyIDWithLessThan64Characters",
            "messageType": "APIStateRequest"
        }   

        await self.send_message(message_data)

    async def get_expressions(self):
        message_data = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
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

    async def set_expression(self, expression, val):

        message_data = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
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
            "requestID": "SomeID",
            "messageType": "InjectParameterDataRequest",
            "data": {
                "mode": "set",
                "parameterValues": params
            }
        }

        return await self.send_message(message_data)
        
    async def eye_movement(self, x, y):
        params =  [
                    {"id": "EyeLeftX", "value": x},
                    {"id": "EyeLeftY", "value": y}
                ]
        
        await self.set_parameters(params)

    async def head_movement(self, x, y, z):
        params =  [
                    {"id": "FaceAngleX", "value": x},
                    {"id": "FaceAngleY", "value": y},
                    {"id": "FaceAngleZ", "value": z}       
                ]
        
        await self.set_parameters(params)
    
    async def vts(self, queue):

        ping = time.time()

        async with websockets.connect(self.url) as self.ws:

            #Authentification is required to connect
            await self.authenticate()

            #Gets all expressions in model
            self.expressions = await self.get_expressions()

            #Sets all expressions to false
            for expression in self.expressions:
                if expression.val == True:
                    await self.set_expression(expression.name, expression.toggle())

            while True:
                #Faster than main loop to deal with API calls before the queue fills
                await asyncio.sleep(.001)

                if not queue.empty():
                    item = await queue.get()

                    if item is None:
                        break
                        
                    #toggle without knowing the value of the expression
                    elif item["state"] == "toggle expression" and "expression" in item:

                        expression = [expression for expression in self.expressions if expression.name == item["expression"]]

                        if expression != []:
                            await self.set_expression(expression[0].name, expression[0].toggle())

                    #toggle expression with value, is ignored if value is already set in expression
                    elif item["state"] == "set expression" and "expression" in item and "val" in item:

                        expression = [expression for expression in self.expressions if expression.name == item["expression"]]

                        if expression != [] and item["val"] != expression[0].val:
                            await self.set_expression(expression[0].name, expression[0].toggle())

                    #set eyes values with x and y
                    elif item["state"] == "eye movement" and "val" in item:
                        values = item["val"]
                        if "x" in values and "y" in values:
                            await self.eye_movement(values["x"], values["y"])

                    #set head values with x, y and z
                    elif item["state"] == "head movement" and "val" in item:
                        values = item["val"]
                        if "x" in values and "y" in values and "z" in values:
                            await self.head_movement(values["x"], values["y"], values["z"])

                    #reset pingpong
                    ping = time.time() + 5
                
                #prevents disconnect due to inactivity, it disconnects after 20 seconds or so.
                elif time.time() > ping:
                    await self.pingpong()
                    ping = time.time() + 5
