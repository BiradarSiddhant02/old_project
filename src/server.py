import os
import asyncio
import websockets
import threading
import json
import re

from websocket_server import WebsocketServer



class Node:
    def __init__ (self, coordinates, dist = float("inf")):
        
        self.coordinates = coordinates
        self.dist = dist
        self.linkedTo = []
        self.previous = None
        self.used = False

    def connect(self, node):
        self.linkedTo.append(node)

    

class Graph:
    def __init__ (self):
        self.nodes = []
        self.makeAllNodes()
        self.removeObstacles()
        self.makeLinks()

    def makeAllNodes(self):
        for x in range(1,12):
            for z in range(1,12):
                self.nodes.append(Node([x,z]))

    def removeObstacles(self):
        for x in range(3,10):
            for z in [3,5]:
                for node in self.nodes:
                    if node.coordinates == [x,z]:
                        self.nodes.remove(node)
        for x in [3,5,7,9]:
            for z in [7,8,9]:
                for node in self.nodes:
                    if node.coordinates == [x,z]:
                        self.nodes.remove(node)

    def makeLinks(self):
        for node in self.nodes:
            for node2 in self.nodes:
                if node2.coordinates == [node.coordinates[0]+1,node.coordinates[1]] or node2.coordinates == [node.coordinates[0]-1,node.coordinates[1]] or node2.coordinates == [node.coordinates[0],node.coordinates[1]+1] or node2.coordinates == [node.coordinates[0],node.coordinates[1]-1]:
                    node.connect(node2)

    def setBots(self, bots, start):
        for node in self.nodes:
            for bot in bots:
                if node.coordinates == bot.coordinates:
                    if not bot.coordinates == start:
                        node.used = True

    def searchNode(self, searchCoord):
        for node in self.nodes:
            if node.coordinates == searchCoord:
                return node

    def clearUsed(self):
        for node in self.nodes:
            node.dist = float("inf")
            node.previous = None
            node.used = False

class Dijkstra:
    def __init__(self):
        self.graph = Graph()
        
    def searchRoute(self, bots, start, finish):
        self.graph.clearUsed()
        self.graph.setBots(bots, start)

        print(start)
        startNode = self.graph.searchNode(start)
        startNode.dist = 0
        endNode = self.graph.searchNode(finish)

        nodeCounter = 0
        while True:
            if nodeCounter == len(self.graph.nodes): 
                nodeCounter = 0
            current = self.graph.nodes[nodeCounter]
            if not current.used:
                for node in self.graph.nodes:
                    if not node.used:
                        if node.dist < current.dist:
                            current = node
                        if current == endNode and endNode != None:
                            return self.getLastCoord(endNode)

                for link in current.linkedTo:
                    if link in self.graph.nodes:
                        dist = current.dist + 1
                        if dist < link.dist:
                            link.dist = dist
                            link.previous = current
            
            current.used = True
            nodeCounter += 1

    def getLastCoord(self, endNode):
        lastNode = endNode.previous
        path = []
        while lastNode:
            # print(lastNode.coordinates)       #print whole route
            path.append(lastNode.coordinates)
            lastNode = lastNode.previous

        if len(path) == 1:
            return endNode.coordinates
        return path[-2]

class Bot:
    def __init__ (self, id, coordinates):
        self.id = id
        self.coordinates = coordinates


class Server:
    def __init__(self):
        self.websocket_server = WebsocketServer()
        self.webotCoordinates = [ (0,0) for x in range(0, 5) ]
        self.oldWebotCoordinates = [ (0,0) for x in range(0, 5) ]
        self.obstacleStack = []
        self.webotInstructions = [[],[],[],[],[]]
        self.pathPlanning = Dijkstra()
        
        self.bots = []

    async def start_websocket_server(self):
        async with websockets.serve(lambda websocket, path: self.websocket_server.websocket_server(websocket, path), "localhost", 8765):
            await asyncio.Future()  # Run the WebSocket server forever
    
    
        #The character 'O' is supposed to represent an open spot where the robots are capable of driving.
        #I also made the array from 0 to 11 so I can address it with the received coordinates from webots or the website.
        self.obstacleMap = [ [ 'O' for x in range (0, 13) ] for y in range (0, 13) ]

    def get_port(self):
        return os.getenv('WS_PORT', '8765')

    def get_host(self):
        return os.getenv('WS_HOST', 'localhost')


    def start(self):
        print('start')
        #websockets.serve(self.handler, 'localhost', 8765)
        websockets.serve(lambda websocket, path: self.handler(websocket, path), "localhost", 8765)

    def handler(self, websocket, path):
        print('hanlder')
        try:
            print("try handler")
            for message in websocket:
                print ('server received : ', message)
                packet = json.loads(message)

                #Filter the messages here. Packet is an list with all the transferred data.
                if packet['instruction'] == "send_coordinate":
                    
                    #Little bit of a mess, but it works I suppose.
                    individualCoordinate = re.findall(r"[\w']+", str(packet['content']))
                    newCoordinates = (individualCoordinate[0], individualCoordinate[1])
                    if(newCoordinates == self.webotCoordinates[packet['sender']]):
                        self.oldWebotCoordinates[packet['sender']] = self.webotCoordinates[packet['sender']];    
                    else:
                        self.oldWebotCoordinates[packet['sender']] = self.webotCoordinates[packet['sender']];
                        self.webotCoordinates[packet['sender']] = newCoordinates;
                        for rows in range (11):
                            for cols in range (11):
                                if(self.obstacleMap[rows][cols] == packet['sender']):
                                    self.obstacleMap[rows][cols] = 'O'
                                    break
                        self.obstacleMap[int(individualCoordinate[1])][int(individualCoordinate[0])] = packet['sender'];
                    if(self.webotInstructions[int(packet['sender'])] == self.webotCoordinates[int(packet['sender'])]):
                        #self.webotInstructions[int(packet['sender'])] = []
                        data = '{"instruction":"response", "sender":"server", "content":"Goal reached"}'
                        try:
                            pass
                            #self.webotInstructions[int(packet['sender'])]
                        except:
                            print("lol it went wrong")
                    else:
                        try:
                            xb = int(self.webotCoordinates[int(packet['sender'])][0])
                            yb = int(self.webotCoordinates[int(packet['sender'])][1])
                            xd = int(self.webotInstructions[int(packet['sender'])][0])
                            yd = int(self.webotInstructions[int(packet['sender'])][1])
                            print(xb, yb)
                            print(xd, yd)
                            walkToCoord = self.pathPlanning.searchRoute(self.bots, [xb,yb], [xd,yd])
                            print(walkToCoord)
                            xpos = walkToCoord[0]
                            ypos = walkToCoord[1]
                            data = '{"instruction":"response_instr", "sender":"server", "content":"'+ str(xpos) + "," + str(ypos) + '"}'
                        except:
                            data = '{"instruction":"response_instr", "sender":"server", "content":"No instructions"}'
                        
                            
                    
                            
                    # if(self.webotInstructions[int(packet['sender'])] == self.webotCoordinates[int(packet['sender'])]):
                    #     self.webotInstructions[int(packet['sender'])].clear()
                    websocket.send(data) 
                elif packet['instruction'] == "request_pos_update":
                    #Convert the tuple of coordinates to a string
                    websocket.send('{"instruction":"response_pos_update", "sender":"server", "content":"webot-'+ str(packet['content'])
                            + str(self.webotCoordinates[packet['content']]) + str(self.oldWebotCoordinates[packet['content']]) + '"}')
                    

                elif packet['instruction'] == "send_obstacle":
                    individualCoordinate = re.findall(r"[\w']+", str(packet['content']))
                    if(self.obstacleMap[int(individualCoordinate[1])][int(individualCoordinate[0])] == 'O'):
                        self.obstacleMap[int(individualCoordinate[1])][int(individualCoordinate[0])] = 'X'
                        self.obstacleStack.append(packet['content'])
                    data = '{"instruction":"response", "sender":"server", "content":"Obstacle observed"}'
                    websocket.send(data) 

            
                elif packet['instruction'] == "request_obs":
                    try:
                        data = '{"instruction":"add_obs", "sender":"server", "content":"'+ self.obstacleStack.pop() +'"}'

                    #When the list is empty, it'll pop() will throw an exception that I catch and then return an empty string instead.
                    except:
                        data = '{"instruction":"add_obs", "sender":"server", "content":""}'
                        websocket.send(data)

                elif packet['instruction'] == "request_instr": 
                    if(len(self.webotInstructions[int(packet['sender'])]) != 0):
                        xb = int(self.webotCoordinates[int(packet['sender'])][0])
                        yb = int(self.webotCoordinates[int(packet['sender'])][1])
                        xd = int(self.webotInstructions[int(packet['sender'])][0])
                        yd = int(self.webotInstructions[int(packet['sender'])][1])
                        walkToCoord = self.pathPlanning.searchRoute(self.bots, [xb,yb], [xd,yd])
                        print(walkToCoord)
                        xpos = walkToCoord[0]
                        ypos = walkToCoord[1]
                        data = '{"instruction":"response_instr", "sender":"server", "content":"'+ str(xpos) + "," + str(ypos) + '"}'
                        print(data)
                    else:
                        data = '{"instruction":"response_instr", "sender":"server", "content":""}' 
                        websocket.send(data) 
                        

                elif packet['instruction'] == "changePos":
                    numbers = packet['content'].split(',')
                    
                    self.webotInstructions[int(numbers[0])] = (str(numbers[1]), str(numbers[2]))
                    #walkToCoord = self.pathPlanning.searchRoute(self.bots, [1,2], [7,4])

                    #await websocket.send(data)
                elif packet['instruction'] == "stopwebots":
                   
                    self.webotInstructions = [[],[],[],[],[]]
                    #walkToCoord = self.pathPlanning.searchRoute(self.bots, [1,2], [7,4])

                    #await websocket.send(data)
                    
        except:
            print("Something happened")
            
          


if __name__ == '__main__':
    var = Server()
    threading.Thread(target=asyncio.run, args=(var.start_websocket_server(),)).start()
    #ws = Server()
    #asyncio.get_event_loop().run_until_complete(ws.start())
   #asyncio.get_event_loop().run_forever()


