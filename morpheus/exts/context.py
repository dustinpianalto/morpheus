from morpheus.core.client import Client
from morpheus.core.room import Room

class Context:
    def __init__(self, client: Client, room: Room, prefix: str, sender: str, ):
        self.client: Client
