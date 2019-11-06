from morpheus.core.client import Client
from morpheus.core.room import Room
from morpheus.core.events import RoomEvent
from morpheus.core.content import ContentBase


class Context:
    def __init__(self, client: Client, room: Room, calling_prefix: str, sender: str, event: RoomEvent, content: ContentBase, called_with: str, body: str):
        self.client: Client = client
        self.room: Room = room
        self.calling_prefix: str = calling_prefix
        self.sender: str = sender  # TODO once the User class is created change this to type User
        self.event: RoomEvent = event
        self.content: ContentBase = content
        self.called_with: str = called_with
        self.body: str = body
        self.extra_params: list = []

    async def send_text(self, body: str, formatted_body: str = None, format_type: str = 'org.matrix.custom.html'):
        await self.client.send_text(self.room, body, formatted_body, format_type)

    @classmethod
    def get_context(cls, event: RoomEvent, calling_prefix: str, called_with: str, body: str):
        return cls(event.client, event.room, calling_prefix, event.sender, event, event.content, called_with, body)
