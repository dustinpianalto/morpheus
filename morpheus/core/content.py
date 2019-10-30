from dataclasses import dataclass, field
from typing import Optional, List, Dict

from .utils import (
    EncryptedFile,
    ImageInfo,
    FileInfo,
    AudioInfo,
    VideoInfo,
    LocationInfo,
    PreviousRoom,
    Invite,
    ReactionRelation,
    notification_power_levels_default_factory
)


@dataclass
class ContentBase:
    pass


@dataclass
class MessageContentBase(ContentBase):
    body: str
    msgtype: str


@dataclass
class MTextContent(MessageContentBase):
    format: Optional[str] = None
    formatted_body: Optional[str] = None
    msgtype = "m.text"


@dataclass
class MEmoteContent(MTextContent):
    msgtype = "m.emote"


@dataclass
class MNoticeContent(MTextContent):
    msgtype = "m.notice"


@dataclass
class MImageContent(MessageContentBase):
    msgtype = "m.image"
    info: ImageInfo
    url: Optional[str] = None
    file: Optional[EncryptedFile] = None


@dataclass
class MFileContent(MessageContentBase):
    msgtype = "m.file"
    filename: str
    info: FileInfo
    url: Optional[str] = None
    file: Optional[EncryptedFile] = None


@dataclass
class MAudioContent(MessageContentBase):
    msgtype = "m.audio"
    info: AudioInfo
    url: Optional[str] = None
    file: Optional[EncryptedFile] = None


@dataclass
class MLocationContent(MessageContentBase):
    msgtype = "m.location"
    geo_uri: str
    info: LocationInfo


@dataclass
class MVideoContent(MessageContentBase):
    msgtype = "m.video"
    info: VideoInfo
    url: Optional[str] = None
    file: Optional[EncryptedFile] = None


@dataclass
class PresenceContent(ContentBase):
    presence: str
    last_active_ago: int
    currently_active: bool
    avatar_url: Optional[str] = None
    displayname: Optional[str] = None
    status_message: Optional[str] = None


@dataclass
class MRoomAliasesContent(ContentBase):
    aliases: List[str]


@dataclass
class MRoomCanonicalAliasContent(ContentBase):
    alias: str


@dataclass
class MRoomCreateContent(ContentBase):
    creator: str
    room_version: Optional[str] = "1"
    m_federate: Optional[bool] = True
    predecessor: Optional[PreviousRoom] = None


@dataclass
class MRoomJoinRulesContent(ContentBase):
    join_rule: str


@dataclass
class MRoomMemberContent(ContentBase):
    membership: str
    is_direct: bool = False
    third_party_invite: Optional[Invite] = None
    avatar_url: Optional[str] = None
    displayname: str = None
    inviter: str = None


@dataclass
class MRoomPowerLevelsContent(ContentBase):
    ban: int = 50
    events: Dict[str, int] = field(default_factory=dict)
    events_default: int = 0
    invite: int = 50
    kick: int = 50
    redact: int = 50
    state_default: int = 50
    users: Dict[str, int] = field(default_factory=dict)
    users_default: int = 0
    notifications: Dict[str, int] = field(default_factory=notification_power_levels_default_factory)


@dataclass
class MRoomRedactionContent(ContentBase):
    reason: str


@dataclass
class MRoomRelatedGroupsContent(ContentBase):
    groups: List[str]


@dataclass
class MRoomTopicContent(ContentBase):
    topic: str


@dataclass
class MRoomNameContent(ContentBase):
    name: str


@dataclass
class MRoomHistoryVisibilityContent(ContentBase):
    history_visibility: str


@dataclass
class MRoomBotOptionsContent(ContentBase):
    options: Dict[str, dict]


@dataclass
class MReactionContent(ContentBase):
    relation: ReactionRelation


@dataclass
class MRoomAvatarContent(ContentBase):
    url: str


@dataclass
class MRoomGuestAccessContent(ContentBase):
    guest_access: str


content_dispatcher = {
    "m.text": MTextContent,
    "m.audio": MAudioContent,
    "m.emote": MEmoteContent,
    "m.notice": MNoticeContent,
    "m.image": MImageContent,
    "m.file": MFileContent,
    "m.location": MLocationContent,
    "m.video": MVideoContent,
    "m.presence": PresenceContent,
    "m.room.aliases": MRoomAliasesContent,
    "m.room.canonical_alias": MRoomCanonicalAliasContent,
    "m.room.create": MRoomCreateContent,
    "m.room.join_rules": MRoomJoinRulesContent,
    "m.room.member": MRoomMemberContent,
    "m.room.power_levels": MRoomPowerLevelsContent,
    "m.room.redaction": MRoomRedactionContent,
    "m.room.related_groups": MRoomRelatedGroupsContent,
    "m.room.topic": MRoomTopicContent,
    "m.room.name": MRoomNameContent,
    "m.room.history_visibility": MRoomHistoryVisibilityContent,
    "m.room.bot.options": MRoomBotOptionsContent,
    'm.reaction': MReactionContent,
    'm.room.avatar': MRoomAvatarContent,
    'm.room.guest_access': MRoomGuestAccessContent,
}
