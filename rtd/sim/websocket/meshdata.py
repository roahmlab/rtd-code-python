import json
import base64
import numpy as np
import uuid
import random

class MeshData:
    def __init__(self):
        self.VerticesCount = 0
        self.IndicesCount = 0
        self.Vertices = []
        self.Color = []
        self.UV0 = []
        self.UV1 = []
        self.IndicesData = []
        self.ExtraInfo = ""
        self.Name = ""
        self.GUID = ""
        self.CollisionGUID = ""
        self.ParentName = ""
        self.ParentGUID = ""
        self.ChildName = ""
        self.ChildGUID = ""
        self.frame_id = ""
        self.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.rotation = {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 0.0}
        self.scale = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        

    def serialize(self):
        data = {
            "VerticesCount": self.VerticesCount,
            "IndicesCount": self.IndicesCount,
            "Vertices": self.Vertices,
            "Color": self.Color,
            "UV0": self.UV0,
            "UV1": self.UV1,
            "IndicesData": self.IndicesData,
            "ExtraInfo": self.ExtraInfo,
            "Name": self.Name,
            "GUID": self.GUID,
            "CollisionGUID": self.CollisionGUID,
            "ParentName": self.ParentName,
            "ParentGUID": self.ParentGUID,
            "ChildName": self.ChildName,
            "ChildGUID": self.ChildGUID,
            "frame_id": self.frame_id,
            "position": {"x": self.position[0], "y": self.position[1], "z": self.position[2]},
            "rotation": {"x": self.rotation[0], "y": self.rotation[1], "z": self.rotation[2], "w": self.rotation[3]},
            "scale": {"x": self.scale[0], "y": self.scale[1], "z": self.scale[2]}
        }
        return json.dumps(data)
        
        
    def serialize64(self):
        data = {
            "VerticesCount": self.VerticesCount,
            "IndicesCount": self.IndicesCount,
            "ExtraInfo": self.ExtraInfo,
            "Name": self.Name,
            "GUID": self.GUID,
            "ParentGUID": self.ParentGUID,
            "ParentName": self.ParentName,
            "ChildGUID": self.ChildGUID,
            "ChildName": self.ChildName,
            "CollisionGUID": self.CollisionGUID,
            "frame_id": self.frame_id,
            "position": {"x": self.position["x"], "y": self.position["y"], "z": self.position["z"]},
            "rotation": {"x": self.rotation["x"], "y": self.rotation["y"], "z": self.rotation["z"], "w": self.rotation["w"]},
            "scale": {"x": self.scale["x"], "y": self.scale["y"], "z": self.scale["z"]}
        }

        if self.Vertices:
            data["VerticesBase64"] = self._encode_base64(np.array(self.Vertices, dtype=np.float32))
        if self.Color:
            data["ColorBase64"] = self._encode_base64(np.array(self.Color, dtype=np.float32))
        if self.UV0:
            data["UV0Base64"] = self._encode_base64(np.array(self.UV0, dtype=np.float32))
        if self.UV1:
            data["UV1Base64"] = self._encode_base64(np.array(self.UV1, dtype=np.float32))
        if self.IndicesData:
            data["IndicesDataBase64"] = self._encode_base64(np.array(self.IndicesData, dtype=np.uint32))

        return json.dumps(data)


    def deserialize(json_str):
        data = json.loads(json_str)
        mesh_data = MeshData()

        # Deserialize attributes from JSON data
        mesh_data.VerticesCount = data.get("VerticesCount", 0)
        mesh_data.IndicesCount = data.get("IndicesCount", 0)
        mesh_data.Vertices = data.get("Vertices", [])
        mesh_data.Color = data.get("Color", [])
        mesh_data.UV0 = data.get("UV0", [])
        mesh_data.UV1 = data.get("UV1", [])
        mesh_data.IndicesData = data.get("IndicesData", [])
        mesh_data.ExtraInfo = data.get("ExtraInfo", "")
        mesh_data.Name = data.get("Name", "")
        mesh_data.GUID = data.get("GUID", "")
        mesh_data.CollisionGUID = data.get("CollisionGUID", "")
        mesh_data.ParentName = data.get("ParentName", "")
        mesh_data.ParentGUID = data.get("ParentGUID", "")
        mesh_data.ChildName = data.get("ChildName", "")
        mesh_data.ChildGUID = data.get("ChildGUID", "")
        mesh_data.frame_id = data.get("frame_id", "")
        mesh_data.position = data.get("position", mesh_data.position)
        mesh_data.rotation = data.get("rotation", mesh_data.rotation)
        mesh_data.scale = data.get("scale", mesh_data.scale)

        return mesh_data

    def deserialize64(json_str):
        data = json.loads(json_str)
        mesh_data = MeshData()

        mesh_data.VerticesCount = data.get("VerticesCount", 0)
        mesh_data.IndicesCount = data.get("IndicesCount", 0)
        mesh_data.ExtraInfo = data.get("ExtraInfo", "")
        mesh_data.Name = data.get("Name", "")
        mesh_data.GUID = data.get("GUID", "")
        mesh_data.ParentGUID = data.get("ParentGUID", "")
        mesh_data.ParentName = data.get("ParentName", "")
        mesh_data.ChildGUID = data.get("ChildGUID", "")
        mesh_data.ChildName = data.get("ChildName", "")
        mesh_data.CollisionGUID = data.get("CollisionGUID", "")
        mesh_data.frame_id = data.get("frame_id", "")

        # Deserialize position, rotation, and scale
        position_data = data.get("position", {})
        mesh_data.position["x"] = position_data.get("x", 0.0)
        mesh_data.position["y"] = position_data.get("y", 0.0)
        mesh_data.position["z"] = position_data.get("z", 0.0)

        rotation_data = data.get("rotation", {})
        mesh_data.rotation["x"] = rotation_data.get("x", 0.0)
        mesh_data.rotation["y"] = rotation_data.get("y", 0.0)
        mesh_data.rotation["z"] = rotation_data.get("z", 0.0)
        mesh_data.rotation["w"] = rotation_data.get("w", 0.0)

        scale_data = data.get("scale", {})
        mesh_data.scale["x"] = scale_data.get("x", 0.0)
        mesh_data.scale["y"] = scale_data.get("y", 0.0)
        mesh_data.scale["z"] = scale_data.get("z", 0.0)
        
        if "VerticesBase64" in data:
            mesh_data.Vertices = mesh_data._decode_base64_to_float(data["VerticesBase64"])
        if "ColorBase64" in data:
            mesh_data.Color = mesh_data._decode_base64_to_float(data["ColorBase64"])
        if "UV0Base64" in data:
            mesh_data.UV0 = mesh_data._decode_base64_to_float(data["UV0Base64"])
        if "UV1Base64" in data:
            mesh_data.UV1 = mesh_data._decode_base64_to_float(data["UV1Base64"])
        if "IndicesDataBase64" in data:
            mesh_data.IndicesData = mesh_data._decode_base64_to_uint32(data["IndicesDataBase64"])


        return mesh_data

    def _encode_base64(self, data):
        return base64.b64encode(data.tobytes()).decode('utf-8')

    def _decode_base64_to_float(self, encoded_str):
        bytes_data = base64.b64decode(encoded_str)
        return np.frombuffer(bytes_data, dtype=np.float32).tolist()

    def _decode_base64_to_uint32(self, encoded_str):
        bytes_data = base64.b64decode(encoded_str)
        return np.frombuffer(bytes_data, dtype=np.uint32).tolist()

    @staticmethod
    def generate_random_double(min_val, max_val):
        return random.uniform(min_val, max_val)

    @staticmethod
    def generate_random_uuid():
        return str(uuid.uuid4())

    # Additional utility and conversion methods as needed


if __name__ == '__main__':
    # Create an instance of MeshData
    original_mesh_data = MeshData()
    # Define vertices (8 corners of a cube)
    original_mesh_data.Vertices = [
        # Front face
        -1.0, -1.0,  1.0,  # Bottom-left
            1.0, -1.0,  1.0,  # Bottom-right
            1.0,  1.0,  1.0,  # Top-right
        -1.0,  1.0,  1.0,  # Top-left
        # Back face
        -1.0, -1.0, -1.0,
            1.0, -1.0, -1.0,
            1.0,  1.0, -1.0,
        -1.0,  1.0, -1.0
    ]

    # Assign a color to each vertex (RGB, simple white color for all)
    original_mesh_data.Color = [1.0, 1.0, 1.0] * 8  # Repeating white color for each vertex

    # Assign UV coordinates to each vertex (2D coordinates, 0.0 to 1.0)
    original_mesh_data.UV0 = [0.0, 0.0] * 8  # Repeating UV coordinates for each vertex
    original_mesh_data.UV1 = [0.0, 0.0] * 8

    # Define the indices for the 12 triangles (2 triangles per face)
    original_mesh_data.IndicesData = [
        # Front face
        0, 1, 2, 2, 3, 0,
        # Right face
        1, 5, 6, 6, 2, 1,
        # Back face
        7, 6, 5, 5, 4, 7,
        # Left face
        4, 0, 3, 3, 7, 4,
        # Bottom face
        4, 5, 1, 1, 0, 4,
        # Top face
        3, 2, 6, 6, 7, 3
    ]

    # Populate with test data (you can use random data or set specific values)
    #original_mesh_data.VerticesCount = 10

    # Serialize the data
    #serialized_data = original_mesh_data.serialize64()

    # Deserialize the data
    #deserialized_mesh_data = MeshData.deserialize64(serialized_data)

    ## Verify the results
    #def verify_mesh_data(original, deserialized):
    #    assert original.VerticesCount == deserialized.VerticesCount
    #    assert original.IndicesCount == deserialized.IndicesCount
    #
    #    # Comparing lists
    #    assert original.Vertices == deserialized.Vertices
    #    assert original.Color == deserialized.Color
    #    assert original.UV0 == deserialized.UV0
    #    assert original.UV1 == deserialized.UV1
    #    assert original.IndicesData == deserialized.IndicesData
    #
    #    # Comparing string attributes
    #    assert original.ExtraInfo == deserialized.ExtraInfo
    #    assert original.Name == deserialized.Name
    #    assert original.GUID == deserialized.GUID
    #    assert original.CollisionGUID == deserialized.CollisionGUID
    #    assert original.ParentName == deserialized.ParentName
    #    assert original.ParentGUID == deserialized.ParentGUID
    #    assert original.ChildName == deserialized.ChildName
    #    assert original.ChildGUID == deserialized.ChildGUID
    #    assert original.frame_id == deserialized.frame_id
    #
    #    # Comparing position, rotation, and scale
    #    assert original.position == deserialized.position
    #    assert original.rotation == deserialized.rotation
    #    assert original.scale == deserialized.scale
    #
    ## Run the verification
    #verify_mesh_data(original_mesh_data, deserialized_mesh_data)

    #print("Test passed successfully!")