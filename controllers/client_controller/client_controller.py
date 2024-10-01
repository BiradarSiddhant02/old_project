import json
import asyncio
import websockets

import time
import threading

from  controller  import  Supervisor
WEBOTID = 4
instructions = []

#Websocket function
async def handler(packet, rec):
    try:
        async with websockets.connect('localhost:8765') as websocket:
            await websocket.send(packet)
            response = await websocket.recv()
            print(response)
            packet = json.loads(response)
            if(packet['instruction'] == "response_instr"):
                if(packet['content'] != ""):
                    coordinates = packet['content'].split(',')
                    print(coordinates)
                    coordinates[0] = float(int(coordinates[0]) / 10)
                    coordinates[1] = float(int(coordinates[1]) / 10)
                    if pos[0] > coordinates[0]:
                        led[0].set(0)
                        led[1].set(0)
                        led[2].set(0)
                        led[3].set(1)
                    if pos[0] < coordinates[0]:
                        led[0].set(0)
                        led[1].set(1)
                        led[2].set(0)
                        led[3].set(0)
                    if pos[2] > coordinates[1]:
                        led[0].set(1)
                        led[1].set(0)
                        led[2].set(0)
                        led[3].set(0)
                    if pos[2] < coordinates[1]:
                        led[0].set(0)
                        led[1].set(0)
                        led[2].set(1)
                        led[3].set(0)
                    pos[0] = coordinates[0]
                    pos[2] = coordinates[1]
    except:
        print("Something went wrong.")
        return



def receive():
    x = (int((pos[X]*10)+0.5))
    z = (int((pos[Z]*10)+0.5))
    data = '{"instruction":"request_instr", "sender":'+ str(WEBOTID) + ', "content":"' + str(x) + ',' + str(z) + '"}'
    asyncio.get_event_loop().run_until_complete(handler(data, 1))



def sendCoordinates(x, y):
    data = '{"instruction":"send_coordinate", "sender":'+ str(WEBOTID) + ', "content":"(' + str(x) + ',' + str(y) + ')"}'
    asyncio.get_event_loop().run_until_complete(handler(data, 0))

def sendObstacle(x, y):
    data = '{"instruction":"send_obstacle", "sender":'+ str(WEBOTID) + ', "content":"(' + str(x) + ',' + str(y) + ')"}'
    asyncio.get_event_loop().run_until_complete(handler(data, 0))


# print(response.body)
# create  the  Robot  instance
robot = Supervisor ()
supervisorNode = robot.getSelf ()
hitted = False
steps = 1

Z = 2
X = 0
# get the  time  step of the  current  world2
timestep = int(robot.getBasicTimeStep ())
# calculate a multiple  of  timestep  close to one  second5
duration = (1000  //  timestep) * timestep

led = []

ledNames = ['led_forward', 'led_right', 'led_behind', 'led_left']
for i in range(4):
    led.append(robot.getDevice(ledNames[i]))

ds = []

dsNames = ['ds_forward', 'ds_right', 'ds_behind', 'ds_left']
for i in range(4):
    ds.append(robot.getDevice(dsNames[i]))
    ds[i].enable(timestep)
pos = supervisorNode.getPosition()
pos[0] = 0.1;
pos[2] = 1.1;

# execute  every  second
while robot.step(duration) !=  -1:


    # for i in range(4):
        # print("position", ds[i].getValue())
    x = (int((pos[X]*10)+0.5))
    z = (int((pos[Z]*10)+0.5))
    sendCoordinates(x, z)
    receive()
    #Block for checking wether its hitting an obstacle.
    for i in range(4):
        if ds[i].getValue() < 800.0:
            # led[i].set(1)
            if (i == 0):
                sendObstacle((int((pos[X]*10)+0.5)), (int((pos[Z]*10)+0.5)-1))
            elif (i == 1):
                sendObstacle((int((pos[X]*10)+0.5)+1), (int((pos[Z]*10)+0.5)))

            elif (i == 2):
                sendObstacle((int((pos[X]*10)+0.5)), (int((pos[Z]*10)+0.5)+1))

            elif (i == 3):
                sendObstacle((int((pos[X]*10)+0.5)-1), (int((pos[Z]*10)+0.5)))



    trans = supervisorNode.getField("translation")
    trans.setSFVec3f(pos)  #pos
