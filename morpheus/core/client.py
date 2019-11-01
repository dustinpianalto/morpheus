import asyncio
from typing import Union, Optional, Dict

from .api import API, APIConfig
from .room import Room


class Client:
    def __init__(
        self,
        prefix: Union[str, list, tuple],
        homeserver: str = "https://matrixcoding.chat",
    ):
        self.prefix = prefix
        self.homeserver = homeserver
        self.user_id: Optional[str] = None
        self.password: Optional[str] = None
        self.token: Optional[str] = None
        self.rooms: Dict[str, Room] = {}
        self.api: Optional[API] = None
        self.running: bool = False
        self.sync_timeout: int = 30000
        self.sync_since: Optional[str] = None
        self.sync_full_state: bool = False
        self.sync_set_presence: str = "online"
        self.sync_filter: Optional[str] = None
        self.sync_delay: Optional[str] = None
        self.sync_process_dispatcher = {
            "presence": self.process_presence_events,
            "rooms": self.process_room_events,
            "groups": self.process_group_events,
        }
        self.event_dispatchers: Dict[str, callable] = {}
        self.users = []

    async def run(self, user_id: str = None, password: str = None, token: str = None):
        if not password and not token:
            raise RuntimeError("Either the password or a token is required")
        self.user_id = user_id
        self.password = password
        self.token = token
        self.api = API(
            base_url=self.homeserver, user_id=self.user_id, password=self.password, token=self.token
        )
        resp = await self.api.login()
        if resp.get("errcode"):
            raise RuntimeError(resp)
        self.running = True
        while self.running:
            await self.sync()
            if self.sync_delay:
                await asyncio.sleep(self.sync_delay)

    async def sync(self):
        resp = await self.api.get_sync(
            self.sync_filter,
            self.sync_since,
            self.sync_full_state,
            self.sync_set_presence,
            self.sync_timeout,
        )
        if resp.get("errcode"):
            self.running = False
            raise RuntimeError(resp)
        self.sync_since = resp["next_batch"]
        for key, value in resp.items():
            if key == "next_batch":
                self.sync_since = value
            else:
                if key in self.sync_process_dispatcher:
                    func = self.sync_process_dispatcher[key]
                    await func(value)
        return resp

    async def process_presence_events(self, value: dict):
        events = value["events"]
        for event_dict in events:
            event = self.process_event(event_dict)
            # TODO Do something with presence event...

    async def process_room_events(self, value: dict):
        await self.process_room_join_events(value["join"])
        await self.process_room_invite_events(value["invite"])
        await self.process_room_leave_events(value["leave"])

    async def process_room_join_events(self, rooms: dict):
        from morpheus.core.events import StateEvent, MessageEvent
        for room_id, data in rooms.items():
            if room_id not in self.rooms:
                self.rooms[room_id] = Room(room_id, self)
            room = self.rooms[room_id]

            # Process state events and update Room state
            for event_dict in data["state"]["events"]:
                event_dict["room"] = room
                event = self.process_event(event_dict)
                await room.update_state(event)
                handler = self.event_dispatchers.get(event.type)
                if handler:
                    await self.invoke(handler, event)

            # Process timeline
            for event_dict in data["timeline"]["events"]:
                event_dict["room"] = room
                event = self.process_event(event_dict)
                if isinstance(event, StateEvent):
                    await room.update_state(event)
                elif isinstance(event, MessageEvent):
                    if event not in room.message_cache:
                        room.message_cache.append(event)
                handler = self.event_dispatchers.get(event.type)
                if handler:
                    await self.invoke(handler, event)

            # Process ephemeral events
            for event in data['ephemeral']['events']:
                if event['type'] == 'm.receipt':
                    room.update_read_receipts(event['content'])
                    # TODO Update read receipts for users
                elif event['type'] == 'm.typing':
                    # TODO process typing messages
                    pass

    async def process_room_invite_events(self, rooms: dict):
        pass

    async def process_room_leave_events(self, rooms: dict):
        pass

    async def process_group_events(self, value: dict):
        pass

    def process_event(self, event: dict):
        from .events import (
            EventBase,
            RoomEvent,
            StateEvent,
            RedactionEvent,
            MessageEvent,
        )

        if event.get("redacted"):
            return RedactionEvent.from_dict(self, event)
        elif event.get("state_key") is not None:
            return StateEvent.from_dict(self, event)
        elif event["type"] == "m.presence":
            return EventBase.from_dict(self, event)
        elif event["type"] == "m.room.message":
            return MessageEvent.from_dict(self, event)
        else:
            return RoomEvent.from_dict(self, event)

    @staticmethod
    async def invoke(handler: callable, event):
        # handler must be a callable which takes the event as an argument
        await handler(event)

    def register_handler(self, event_type, handler: callable):
        if not callable(handler):
            raise TypeError(f'handler must be a callable not {type(handler)}')
        self.event_dispatchers[event_type] = handler

    async def send_room_message(self, room: Room, content: dict):
        await self.api.room_send(room_id=room.id, event_type='m.room.message', content=content)

    async def send_text(self, room: Room, body: str, formatted_body: str = None, format_type: str = None):
        content = {
            'msgtype': 'm.text',
            'body': body
        }
        if formatted_body and format_type:
            content['format'] = format_type
            content['formatted_body'] = formatted_body

        await self.send_room_message(room=room, content=content)

    # TODO send_emote
    # TODO send_notice
    # TODO send_image
    # TODO send_file
    # TODO send_audio
    # TODO send_location
    # TODO send_video
