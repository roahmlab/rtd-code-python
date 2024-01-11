from rtd.sim import SimulationSystem
from rtd.sim.websocket import PlannerWebSocketClient
import asyncio

async def increment_timer():
    while True:
        await asyncio.sleep(0.01)
        PlannerWebSocketClient.interaction_timestamp += 0.01

class ClientSimulationSystem(SimulationSystem):
    '''
    Base class for client based visual and collision systems 
    '''
    def __init__(self):
        SimulationSystem.__init__(self)
        self.client: PlannerWebSocketClient = PlannerWebSocketClient()
    
    
    def reset(self):
        '''
        Connects to the server and resets the system
        '''
        asyncio.get_event_loop().run_until_complete(self.connect())
        asyncio.get_event_loop().create_task(increment_timer())
        # asyncio.get_event_loop().run_forever()
    
    
    async def connect(self) -> bool:
        '''
        Connects the client to the server, returns whether it connected
        '''
        connected = await self.client.connect('localhost', 9001)
        # asyncio.get_event_loop().run_until_complete(self.client.connect(PlannerWebSocketClient.server_ip, "9001"))
        # asyncio.get_event_loop().create_task(increment_timer())
        # asyncio.get_event_loop().run_forever()
        return connected
    
    
    def disconnect(self):
        '''
        Disconnects the client
        '''
        self.client.disconnect()
        asyncio.get_event_loop().stop()


    async def keep_alive(self, interval=1):
        while True:
            if self.client.ws is None or not self.client.ws.open:
                print("WebSocket is not connected. Cannot send keep-alive message.")
                # Optional: Try to reconnect here
            else:
                try:
                    await self.client.ws.send("hey")
                    print("Keep-alive message sent.")
                except Exception as e:
                    print(f"Failed to send keep-alive message: {e}")
            await asyncio.sleep(interval)  # Wait for the specified interval before sending again