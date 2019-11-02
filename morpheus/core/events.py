from dataclasses import dataclass
from typing import Optional, List

from .client import Client
from .room import Room
from .content import ContentBase
from .utils import ReactionRelation, MessageRelation


@dataclass
class EventBase:
    client: Client
    content: ContentBase
    type: str
    sender: str

    @classmethod
    def from_dict(cls, client: Client, event_dict: dict):
        from .content import content_dispatcher
        if event_dict['type'] == 'm.room.message':
            content_class = content_dispatcher[event_dict['content']['msgtype']]
        else:
            content_class = content_dispatcher[event_dict['type']]

        if event_dict['type'] == 'm.reaction':
            content_dict = {'relation': ReactionRelation(**event_dict['content']['m.relates_to'])}
        elif event_dict['type'] == 'm.room.bot.options':
            content_dict = {'options': event_dict['content']}
        else:
            content_dict = event_dict['content']

        if content_dict.get('m.relates_to'):
            if content_dict['m.relates_to'].get('m.in_reply_to'):
                content_dict['relates_to'] = MessageRelation(
                    event_id=content_dict['m.relates_to']['m.in_reply_to']['event_id']
                )
            del content_dict['m.relates_to']

        if content_dict.get('m.new_content'):
            del content_dict['m.new_content']

        del event_dict['content']

        return cls(
            client=client,
            content=content_class(**content_dict),
            **event_dict
        )


@dataclass
class UnsignedData:
    age: int
    redacted_because: Optional[EventBase] = None
    transaction_id: Optional[str] = None
    invite_room_state: Optional[List[EventBase]] = None


@dataclass
class RoomEvent(EventBase):
    event_id: str
    origin_server_ts: int
    unsigned: UnsignedData
    room: Room


@dataclass
class StateEvent(RoomEvent):
    state_key: str
    age: int = None
    prev_content: Optional[EventBase] = None


@dataclass
class RedactionEvent(RoomEvent):
    redacts: EventBase


@dataclass
class MessageEvent(RoomEvent):
    pass


@dataclass
class PresenceEvent(EventBase):
    pass
