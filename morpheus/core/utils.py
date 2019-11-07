from dataclasses import dataclass
from typing import Optional, List, Dict
from inspect import isawaitable
from collections import OrderedDict


@dataclass
class JSONWebKey:
    key_opts: List[str]
    k: str
    ext: bool = True
    alg: str = "A256CTR"
    kty: str = "oct"


@dataclass
class EncryptedFile:
    url: str
    key: JSONWebKey
    iv: str
    hashes: Dict[str, str]
    v: str = "v2"


@dataclass
class ImageInfoBase:
    h: int
    w: int
    mimetype: str
    size: int


@dataclass
class ImageInfo(ImageInfoBase):
    thumbnail_info: ImageInfoBase
    thumbnail_url: Optional[str] = None
    thumbnail_file: Optional[EncryptedFile] = None


@dataclass
class FileInfo:
    mimetype: str
    size: int
    thumbnail_info: ImageInfoBase
    thumbnail_url: Optional[str] = None
    thumbnail_file: Optional[EncryptedFile] = None


@dataclass
class AudioInfo:
    duration: int
    mimetype: str
    size: int


@dataclass
class LocationInfo:
    thumbnail_info: ImageInfoBase
    thumbnail_url: Optional[str] = None
    thumbnail_file: Optional[EncryptedFile] = None


@dataclass
class VideoInfo(ImageInfoBase):
    duration: int
    thumbnail_info: ImageInfoBase
    thumbnail_url: Optional[str] = None
    thumbnail_file: Optional[EncryptedFile] = None


@dataclass
class PreviousRoom:
    room_id: str
    event_id: str


@dataclass
class Signed:
    mxid: str
    signatures: Dict[str, Dict[str, str]]
    token: str


@dataclass
class Invite:
    display_name: str
    signed: Signed


@dataclass
class ReactionRelation:
    rel_type: str
    event_id: str
    key: str


@dataclass
class MessageRelation:
    event_id: str


async def maybe_coroutine(func, *args, **kwargs):
    f = func(*args, **kwargs)
    if isawaitable(f):
        return await f
    else:
        return f


def notification_power_levels_default_factory():
    return {'room': 50}


class DequeDict(OrderedDict):
    def __init__(self, *args, max: int = 0, **kwargs):
        self._max = max
        super(DequeDict, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        if self._max > 0:
            if len(self) > self._max:
                self.popitem(False)
