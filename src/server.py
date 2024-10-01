import os
import asyncio
import websockets
import json
import re
from websocket_server import WebsocketServer
from dijkstra_algo import Dijkstra

class Server:
    def __init__(self):
        self.websocket_server = WebsocketServer()
        self.webotCoordinates = [(0, 0) for x in range(0, 5)]
        self.oldWebotCoordinates = [(0, 0) for x in range(0, 5)]
        self.obstacleStack = []
        self.webotInstructions = [[], [], [], [], []]
        self.pathPlanning = Dijkstra()
        self.bots = []

    async def start_websocket_server(self):
        async with websockets.serve(self.handler, "localhost", 8765):
            await asyncio.Future()  # Run the WebSocket server forever

    async def handler(self, websocket, path):
        print("handler")
        try:
            async for message in websocket:
                print("server received:", message)
                packet = json.loads(message)
                
                # Filter the messages here. Packet is a list with all the transferred data.
                if packet['instruction'] == "send_coordinate":
                    individualCoordinate = re.findall(r"[\w']+", str(packet['content']))
                    newCoordinates = (individualCoordinate[0], individualCoordinate[1])

                    # Update webot coordinates
                    if newCoordinates != self.webotCoordinates[packet['sender']]:
                        self.oldWebotCoordinates[packet['sender']] = self.webotCoordinates[packet['sender']]
                        self.webotCoordinates[packet['sender']] = newCoordinates
                        # Update obstacle map
                        for rows in range(11):
                            for cols in range(11):
                                if self.obstacleMap[rows][cols] == packet['sender']:
                                    self.obstacleMap[rows][cols] = 'O'
                                    break
                        self.obstacleMap[int(individualCoordinate[1])][int(individualCoordinate[0])] = packet['sender']
                    
                    # Check if goal is reached
                    if self.webotInstructions[int(packet['sender'])] == self.webotCoordinates[int(packet['sender'])]:
                        data = '{"instruction":"response", "sender":"server", "content":"Goal reached"}'
                    else:
                        try:
                            xb, yb = int(self.webotCoordinates[int(packet['sender'])][0]), int(self.webotCoordinates[int(packet['sender'])][1])
                            xd, yd = int(self.webotInstructions[int(packet['sender'])][0]), int(self.webotInstructions[int(packet['sender'])][1])
                            walkToCoord = self.pathPlanning.searchRoute(self.bots, [xb, yb], [xd, yd])
                            xpos, ypos = walkToCoord[0], walkToCoord[1]
                            data = '{"instruction":"response_instr", "sender":"server", "content":"' + str(xpos) + "," + str(ypos) + '"}'
                        except Exception as e:
                            print("Error:", e)
                            data = '{"instruction":"response_instr", "sender":"server", "content":"No instructions"}'
                    
                    await websocket.send(data)

                elif packet['instruction'] == "request_pos_update":
                    await websocket.send('{"instruction":"response_pos_update", "sender":"server", "content":"webot-' + str(packet['content']) +
                                         str(self.webotCoordinates[packet['content']]) + str(self.oldWebotCoordinates[packet['content']]) + '"}')
                elif packet['instruction'] == "send_obstacle":
                    individualCoordinate = re.findall(r"[\w']+", str(packet['content']))
                    if self.obstacleMap[int(individualCoordinate[1])][int(individualCoordinate[0])] == 'O':
                        self.obstacleMap[int(individualCoordinate[1])][int(individualCoordinate[0])] = 'X'
                        self.obstacleStack.append(packet['content'])
                    data = '{"instruction":"response", "sender":"server", "content":"Obstacle observed"}'
                    await websocket.send(data)

                elif packet['instruction'] == "request_obs":
                    try:
                        data = '{"instruction":"add_obs", "sender":"server", "content":"' + self.obstacleStack.pop() + '"}'
                    except IndexError:
                        data = '{"instruction":"add_obs", "sender":"server", "content":""}'
                    await websocket.send(data)

                elif packet['instruction'] == "request_instr":
                    if len(self.webotInstructions[int(packet['sender'])]) != 0:
                        xb = int(self.webotCoordinates[int(packet['sender'])][0])
                        yb = int(self.webotCoordinates[int(packet['sender'])][1])
                        xd = int(self.webotInstructions[int(packet['sender'])][0])
                        yd = int(self.webotInstructions[int(packet['sender'])][1])
                        walkToCoord = self.pathPlanning.searchRoute(self.bots, [xb, yb], [xd, yd])
                        xpos, ypos = walkToCoord[0], walkToCoord[1]
                        data = '{"instruction":"response_instr", "sender":"server", "content":"' + str(xpos) + "," + str(ypos) + '"}'
                        print(data)
                    else:
                        data = '{"instruction":"response_instr", "sender":"server", "content":""}'
                    await websocket.send(data)

                elif packet['instruction'] == "changePos":
                    numbers = packet['content'].split(',')
                    self.webotInstructions[int(numbers[0])] = (str(numbers[1]), str(numbers[2]))
                
                elif packet['instruction'] == "stopwebots":
                    self.webotInstructions = [[], [], [], [], []]

        except Exception as e:
            print("Error:", e)


if __name__ == '__main__':
    server = Server()
    asyncio.run(server.start_websocket_server())
