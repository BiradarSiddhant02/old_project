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
                        if current == endNode and endNode.previous != None:
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

pathPlanning = Dijkstra()

bots = []
# bots.append (Bot (1, [0,10]))
# bots.append (Bot (2, [4,4]))
# bots.append (Bot (3, [10,8]))
# bots.append (Bot (4, [1,2]))

walkToCoord = pathPlanning.searchRoute(bots, [1,1], [10,10])
print(walkToCoord)
walkToCoord2 = pathPlanning.searchRoute(bots, [10,10], [1,1])
print(walkToCoord2)

# print whole map
# for node in pathPlanning.graph.nodes:
#     print(node.coordinates, end='')
#     for node2 in node.linkedTo:
#         print (node2.coordinates, end='')
#     print()