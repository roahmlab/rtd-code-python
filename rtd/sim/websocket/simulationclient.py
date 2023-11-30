import asyncio
import urchin
#import pyassimp
import websockets
import json
import random
import time
import os
import math

from argparse import ArgumentParser

class PlannerWebSocketClient:
    urdf_file_path = ""
    server_ip = "localhost"
    interaction_timestamp = 0.0
    
    def __init__(self):
        self.ws = None
        self.plan_counter = 0
        self.chunk_size = 4096
        self.mesh_data_list = []
        
    async def connect(self, host, port):
        uri = f"ws://{host}:{port}/planner"
        try:
            self.ws = await websockets.connect(uri)
            print("Connected to the server!")
            
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
        
    async def disconnect(self):
        if self.ws:
            await self.ws.close()
            self.ws = None
            print("Disconnected from the server.")

    async def on_open(self):
                # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open before sending message in on_open.")
        else:
            print("WebSocket is already closed before sending message in on_open.")
        print("Connected to Fthe server!")    
        await self.send_mesh_data_list()
        if self.ws.open:
            print("WebSocket is open after sending message in on_open.")
        else:
            print("WebSocket is already closed after sending message in on_open.")

            
    def clear_mesh_data_list(self):
        self.mesh_data_list.clear()

    def add_mesh_data(self, mesh_data):
        self.mesh_data_list.append(mesh_data)

    async def send_mesh_data_list(self):
                # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open before sending message in send_mesh_data_list.")
        else:
            print("WebSocket is already closed before sending message in send_mesh_data_list.")
        if not self.mesh_data_list:
            print("Mesh data list is empty.")
            return

        if self.mesh_data_list:
            await self.send_mesh_data(self.mesh_data_list[0].serialize64(), 1)
                # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open after sending message in send_mesh_data_list.")
        else:
            print("WebSocket is already closed after sending message in send_mesh_data_list.")
            
    async def send_plan(self, GUID):
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open before sending message in send_plan.")
        else:
            print("WebSocket is already closed before sending message in send_plan.")
        print("DEBUG: Sending plan for GUID:", GUID)

        # Generate a new position with random coordinates
        new_position = (random.uniform(0, 10), random.uniform(0, 10), random.uniform(0, 10))

        # Generate a new rotation with random angles (in radians or degrees, depending on your system)
        new_rotation = (random.uniform(0, 2 * math.pi),  # Rotation around X-axis
                        random.uniform(0, 2 * math.pi),  # Rotation around Y-axis
                        random.uniform(0, 2 * math.pi))  # Rotation around Z-axis

        # Call the method to send move object message
        await self.send_move_object_message(GUID, new_position, new_rotation)
        print("DEBUG: Plan sent for GUID:", GUID)
                # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open after sending message in send_plan.")
        else:
            print("WebSocket is already closed after sending message in send_plan.")


    async def send_mesh_data(self, large_message, next_mesh_data_index):
        if self.ws.open:
            print("WebSocket is open before sending message in send_mesh_data.")
        else:
            print("WebSocket is already closed before sending message in send_mesh_data.")
        unique_message_id = "MSG_" + str(time.time())  # Example to generate a unique message ID
        print("unique_message_id = ", unique_message_id)
        chunks = self.break_into_chunks(large_message, unique_message_id)
        await self.send_chunks(chunks, lambda: self.on_all_chunks_sent(next_mesh_data_index))
        if self.ws.open:
            print("WebSocket is open after sending message in send_mesh_data.")
        else:
            print("WebSocket is already closed after sending message in send_mesh_data.")

    def break_into_chunks(self, large_message, message_id):
        # Split the large message into chunks
        chunks = [large_message[i:i + self.chunk_size] for i in range(0, len(large_message), self.chunk_size)]
        total_chunks = len(chunks)
        return [
            {
                "type": "meshdata_chunk",  # Specify the type of message
                "messageId": message_id,
                "chunkIndex": i,
                "totalChunks": total_chunks,
                "data": chunk
            }
            for i, chunk in enumerate(chunks)
        ]

    async def send_chunks(self, chunks, callback):
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open before sending message in send_chunks.")
        else:
            print("WebSocket is already closed before sending message in send_chunks.")
            
        for chunk in chunks:
            chunk_str = json.dumps(chunk)  # Convert the chunk data to a JSON string
            await self.ws.send(chunk_str)  # Send the chunk over WebSocket

        if callback:
            await callback()  # Invoke the callback after all chunks are sent
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open after sending message in send_chunks.")
        else:
            print("WebSocket is already closed after sending message in send_chunks.")

    async def on_all_chunks_sent(self, next_mesh_data_index):
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open before sending message in on_all_chunks_sent.")
        else:
            print("WebSocket is already closed before sending message in on_all_chunks_sent.")
            
        # Check if there are more mesh data to send
        if next_mesh_data_index < len(self.mesh_data_list):
            # Serialize the next mesh data and send it
            next_serialized_mesh_data = self.mesh_data_list[next_mesh_data_index].serialize64()
            await self.send_mesh_data(next_serialized_mesh_data, next_mesh_data_index + 1)
        else:
            # All mesh data have been sent; now send the plan
            await self.send_plan("43253254-32543254-43535432-45325")

        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open after sending message in on_all_chunks_sent.")
        else:
            print("WebSocket is already closed after sending message in on_all_chunks_sent.")

    async def on_message(self, message):
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open before receiving message in on_message.")
        else:
            print("WebSocket is already closed before receiving message in on_message.")
           
        try:
            message_data = json.loads(message)
        except json.JSONDecodeError:
            print("Error decoding JSON message")
            return

        # Extract the message type
        message_type = message_data.get("type")

        # Handle different message types
        if message_type == "moveobjectreceived":
            # Handle move object received message
            
            await self.handle_move_object_received(message_data)
        elif message_type == "acknowledgment":
            # Handle acknowledgment message
            await self.handle_acknowledgment(message_data)
        elif message_type == "feedback":
            # Handle feedback message
            await self.handle_feedback(message_data)
        elif message_type == "collisionAlert":
            # Handle collision alert message
            await self.handle_collision_alert(message_data)
        else:
            # Unknown message type
            print(f"Unknown message type received: {message_type}")
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open after sending receiving message in on_message.")
        else:
            print("WebSocket is already closed after sending message in on_message.")

    async def handle_move_object_received(self, data):
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open before receiving message in handle_move_object_received.")
        else:
            print("WebSocket is already closed before receiving message in handle_move_object_received.")
        await self.send_plan("43253254-32543254-43535432-45325")
        # Add a debug print to confirm the end of the method execution
        print("DEBUG: Completed handling move object received.")
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open after receiving message in handle_move_object_received.")
        else:
            print("WebSocket is already closed after receiving message in handle_move_object_received.")



    async def handle_acknowledgment(self, data):
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open before receiving message in handle_acknowledgment.")
        else:
            print("WebSocket is already closed before receiving message in handle_acknowledgment.")
        await self.send_plan("43253254-32543254-43535432-45325")
        print(f"handle_acknowledgment: {data}")
        message_id = data.get('messageId', 'Unknown')
        await self.send_plan("43253254-32543254-43535432-45325")
        print(f"Acknowledgment received for message ID: {message_id}")
        # Additional handling logic as required
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open after sending receiving message in handle_acknowledgment.")
        else:
            print("WebSocket is already closed after receiving message in handle_acknowledgment.")

    async def handle_feedback(self, data):
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open before receiving message in handle_feedback.")
        else:
            print("WebSocket is already closed before receiving message in handle_feedback.")
        await self.send_plan("43253254-32543254-43535432-45325")
        print(f"handle_feedback: {data}")
        feedback = data.get('data', 'No feedback provided')
        print(f"Feedback received: {feedback}")
        # Additional handling logic as required
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open after sending receiving message in handle_feedback.")
        else:
            print("WebSocket is already closed after receiving message in handle_feedback.")

    async def handle_collision_alert(self, data):
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open before receiving message in handle_collision_alert.")
        else:
            print("WebSocket is already closed receiving sending message in handle_collision_alert.")
        await self.send_plan("43253254-32543254-43535432-45325")
        print(f"handle_collision_alert: {data}")
        details = data.get('details', 'No details provided')
        await self.send_plan("43253254-32543254-43535432-45325")
        print(f"Collision alert: {details}")
        # Additional handling logic as required, such as stopping movements, logging, etc.
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open after receiving message in handle_collision_alert.")
        else:
            print("WebSocket is already closed after receiving message in handle_collision_alert.")

    async def send_move_object_message(self, guid, position, rotation, scale=(1, 1, 1)):
        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open before sending message in send_move_object_message.")
        else:
            print("WebSocket is already closed before sending message in send_move_object_message.")

        if not self.ws or not self.ws.open:
            print("WebSocket connection is not established before sending message in send_move_object_message.")
            return


        # Construct the move object message
        move_object_message = {
            "type": "moveobject",
            "guid": guid,
            "position": {
                "x": position[0],
                "y": position[1],
                "z": position[2]
            },
            "rotation": {
                "x": rotation[0],
                "y": rotation[1],
                "z": rotation[2]
            },
            "scale": {
                "x": scale[0],
                "y": scale[1],
                "z": scale[2]
            }
        }
        # Serialize the message to JSON
        message_json = json.dumps(move_object_message)
        print(f"Sending move object message: {message_json}")


        # Send the message over WebSocket
        try:
            await self.ws.send(message_json)
            print(f"Move object message sent for GUID: {guid}")
        except Exception as e:
            print(f"Failed to send move object message: {e}")

        # Check if the connection is still open after sending the message
        if self.ws.open:
            print("WebSocket is still open after sending message in send_move_object_message.")
        else:
            print("WebSocket disconnected after attempting to send message in send_move_object_message.")


    async def do_read(self):
                # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open before reading message in do_read.")
        else:
            print("WebSocket is already closed before reading message in do_read.")
        try:
            while True:
                message = await self.ws.recv()
                await self.on_message(message)
        except websockets.exceptions.ConnectionClosed as e:
            print(f"WebSocket connection closed: {e}")
            print(f"Code: {e.code}, Reason: {e.reason}")
        except Exception as ex:
            print(f"Unexpected error in do_read: {ex}")
        finally:
            print("WebSocket read loop ended.")
                        # Check WebSocket status before sending
        if self.ws.open:
            print("WebSocket is open after reading message in do_read.")
        else:
            print("WebSocket is already closed after reading message in do_read.")


async def increment_timer():
    while True:
        await asyncio.sleep(0.01)
        PlannerWebSocketClient.interaction_timestamp += 0.01

def replace_package_urls_in_urdf(file_path):
    exe_path = get_executable_path()
    with open(file_path, 'r') as file:
        urdf_content = file.read()

    # Replace 'package://' with the actual executable path
    urdf_content = urdf_content.replace('package://', exe_path + '/')

    return urdf_content

def load_urdf_with_replaced_paths(urdf_file_path):
    # Get the directory of the URDF file
    urdf_directory = os.path.dirname(os.path.abspath(urdf_file_path))

    # Read the content of the URDF file
    with open(urdf_file_path, 'r') as file:
        urdf_content = file.read()

    # Replace the 'package://' with the URDF directory path
    urdf_content = urdf_content.replace('package://', urdf_directory + '/')

    # Write the modified URDF content to a temporary file
    temp_file_path = urdf_directory + '/temp.urdf'
    with open(temp_file_path, 'w') as file:
        file.write(urdf_content)

    # Load the URDF from the modified file
    urdf_robot = urchin.URDF.load(temp_file_path)

    # Optionally, remove the temporary file after loading
    os.remove(temp_file_path)

    return urdf_robot


def get_executable_path():
    return os.path.dirname(os.path.abspath(__file__))

def start_system():
    client = PlannerWebSocketClient()
    asyncio.get_event_loop().run_until_complete(client.connect(PlannerWebSocketClient.server_ip, "9001"))
    asyncio.get_event_loop().create_task(increment_timer())
    asyncio.get_event_loop().run_forever()

def stop_system():
    asyncio.get_event_loop().stop()

def convert_stl_to_mesh_data(file_path, mesh_data, guidstring):
    scene = pyassimp.load(file_path)

    if not scene.meshes:
        print("Error loading file: ", file_path)
        return

    mesh = scene.meshes[0]

    mesh_data.vertices_count = len(mesh.vertices)
    mesh_data.indices_count = len(mesh.faces) * 3
    mesh_data.guid = guidstring

    for vertex in mesh.vertices:
        mesh_data.vertices.extend(vertex)

    for face in mesh.faces:
        if len(face.indices) == 3:
            mesh_data.indices_data.extend(face.indices)

    pyassimp.release(scene)


def convert_collada_to_mesh_data(file_path, mesh_data, guidstring):
    scene = pyassimp.load(file_path)

    if not scene.meshes:
        print("Error loading file: ", file_path)
        return

    for mesh in scene.meshes:
        for vertex in mesh.vertices:
            mesh_data.vertices.extend(vertex)

        if mesh.colors:
            for color in mesh.colors[0]:
                mesh_data.color.extend(color)

        if mesh.texturecoords:
            for uv in mesh.texturecoords[0]:
                mesh_data.uv0.extend(uv[:2])
            if len(mesh.texturecoords) > 1:
                for uv in mesh.texturecoords[1]:
                    mesh_data.uv1.extend(uv[:2])

        for face in mesh.faces:
            if len(face.indices) == 3:
                mesh_data.indices_data.extend(face.indices)

        mesh_data.guid = guidstring

    pyassimp.release(scene)

def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-s", "--server_ip", help="Set server IP", default="localhost")
    parser.add_argument("-u", "--urdf", help="Set URDF file path", default="")
    args = parser.parse_args()

    PlannerWebSocketClient.server_ip = args.server_ip

    PlannerWebSocketClient.urdf_file_path = args.urdf

if __name__ == "__main__":
    parse_arguments()
    start_system()
