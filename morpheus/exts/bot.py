import asyncio
from typing import Union, Optional, Dict

from morpheus.core.client import Client
from morpheus.core.room import Room
from .context import Context


class Bot(Client):
    def __init__(
        self,
        prefix: Union[str, list, tuple],
        homeserver: str = "https://matrixcoding.chat",
    ):
        self.loop = asyncio.get_event_loop()
        super(Bot, self).__init__(prefix=prefix, homeserver=homeserver)

    def run(self, user_id: str = None, password: str = None, token: str = None):
        loop = self.loop or asyncio.get_event_loop()
        loop.run_until_complete(super(Bot, self).run(user_id, password, token))

    async def get_context(self, event):


    async def check_event(self, event):

