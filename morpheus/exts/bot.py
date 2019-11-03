import asyncio
from typing import Union, Optional, Dict, List
from inspect import isawaitable
from argparse import ArgumentParser

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
        self.commands: Dict[str, dict] = {}
        self.aliases: Dict[str, str] = {}

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

    async def process_command(self, event):
        ctx = await self.get_context(event)
        if not ctx:
            return

        command_name = self.aliases.get(ctx.called_with)
        if not command_name:
            return
        command_dict = self.commands.get(command_name)
        if not command_dict:
            del self.aliases[ctx.called_with]
        parser: ArgumentParser = command_dict['parser']
        command = command_dict['command']
        args = parser.parse_args(ctx.body.split(' '))

    def listener(self, name=None):
        def decorator(func):
            self.register_handler(name, func)
        return decorator

    def add_command(self, name: str, func: callable):
        if not callable(func):
            raise TypeError('Command function must be callable')

        if not isawaitable(func):
            raise TypeError('Command function must be a coroutine')

        if not name:
            name = func.__name__

        if name in self.commands:
            raise RuntimeWarning(f'Command {name} has already been registered')

        self.commands[name] = func
