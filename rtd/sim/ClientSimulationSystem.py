from abc import ABCMeta
import asyncio
from rtd.sim.websocket import PlannerWebSocketClient



class ClientSimulationSystem(metaclass=ABCMeta):
    '''
    Base class for client based visual and collision systems 
    '''
    def __init__(self):
        self.time: list[float] = None
        self.time_discretization: float = None
        self.client: PlannerWebSocketClient = PlannerWebSocketClient()
    
    
    def reset(self):
        '''
        Connects to the server and resets the system
        '''
        asyncio.run(self.connect())
    
    
    async def connect(self) -> bool:
        '''
        Connects the client to the server, returns whether it connected
        '''
        connected = await self.client.connect('localhost', 9001)
        return connected
    
    
    def disconnect(self):
        '''
        Disconnects the client
        '''
        self.client.disconnect()


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