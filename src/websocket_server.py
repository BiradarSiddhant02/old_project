import asyncio
import websockets

class WebsocketServer:
    def __init__(self):
        self.websocket = None
    
    async def send_data(self, data):
        # Send data to the WebSocket client
        if self.websocket != None:
            await self.websocket.send(data)

    async def websocket_server(self, websocket, path):
        # Send a welcome message to the WebSocket client
        await self.send_data('Hello')
        self.websocket = websocket

        while True:
            try:
                # Wait for data from the MQTT client
                data = await asyncio.get_event_loop().create_future()
                await asyncio.wait([data])

                # Forward the data to the WebSocket client
                await self.send_data(data.result())
            except websockets.exceptions.ConnectionClosedOK:
                # WebSocket connection was closed
                break
