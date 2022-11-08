from typing import Optional
from datetime import datetime
from masto_git_bridge.config import Config
from masto_git_bridge.models import Account

from mastodon import Mastodon, StreamListener

class Listener(StreamListener):
    def __init__(self, client: Mastodon, config:Optional[Config]=None):
        self.client = client

        if config is None:
            config = Config()

        self.config = config



class Bot:
    def __init__(self, config:Optional[Config]=None):
        self._me = None # type: Optional[Account]

        if config is None:
            config = Config()

        self.config = config
        self.config.LOGDIR.mkdir(exist_ok=True)

        self.client = Mastodon(
            access_token=self.config.MASTO_TOKEN,
            api_base_url=self.config.MASTO_URL
        )

    @property
    def me(self) -> Account:
        if self._me is None:
            self._me = Account(**self.client.me())
        return self._me


