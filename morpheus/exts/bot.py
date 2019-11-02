import asyncio
from typing import Union, Optional, Dict

from morpheus.core.client import Client
from morpheus.core.room import Room
from morpheus.core.utils import maybe_coroutine
from morpheus.core.events import RoomEvent
from morpheus.core.content import MessageContentBase
from .context import Context


class Bot(Client):
    def __init__(
        self,
        prefix: Union[str, list, tuple, callable],
        homeserver: str = "https://matrixcoding.chat",
    ):
        self.loop = asyncio.get_event_loop()
        super(Bot, self).__init__(prefix=prefix, homeserver=homeserver)

    def run(self, user_id: str = None, password: str = None, token: str = None, loop: Optional[asyncio.AbstractEventLoop] = None):
        loop = loop or self.loop or asyncio.get_event_loop()
        loop.run_until_complete(super(Bot, self).run(user_id, password, token, loop=loop))

    async def get_context(self, event: RoomEvent):
        if not isinstance(event.content, MessageContentBase):
            return None

        if callable(self.prefix):
            prefix = await maybe_coroutine(self.prefix, event)
        elif isinstance(self.prefix, (str, list, tuple)):
            prefix = self.prefix
        else:
            raise RuntimeError('Prefix must be a string, list of strings or callable')

        if isinstance(prefix, str):
            return self._get_context(event, prefix)
        elif isinstance(prefix, (list, tuple)):
            prefixes = tuple(prefix)
            for prefix in prefixes:
                try:
                    ctx = self._get_context(event, prefix)
                    if ctx:
                        return ctx
                except TypeError:
                    raise RuntimeError('Prefix must be a string or list of strings')
            else:
                return None
        else:
            raise RuntimeError('Prefix must be a string or list of strings')

    @staticmethod
    def _get_context(event: RoomEvent, prefix: str):
        if not isinstance(event.content, MessageContentBase):
            return None

        raw_body = event.content.body
        if not raw_body.startswith(prefix):
            return None
        raw_body = raw_body.lstrip(prefix)
        called_with, body = raw_body.split(' ', 1)
        return Context.get_context(event, prefix, called_with, body)

    async def check_event(self, event):
        ctx = await self.get_context(event)

    def listener(self, name=None):
        def decorator(func):
            self.register_handler(name, func)
        return decorator
