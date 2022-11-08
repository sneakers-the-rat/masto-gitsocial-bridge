import pdb
from typing import Optional
from datetime import datetime
from masto_git_bridge.config import Config
from masto_git_bridge.models import Account, List
from masto_git_bridge.post import Post, Status
from masto_git_bridge.logger import init_logger
from masto_git_bridge.repo import Repo

from mastodon import Mastodon, StreamListener

class Listener(StreamListener):
    def __init__(self, client: Mastodon, config:Optional[Config]=None):
        super(Listener, self).__init__()
        self.client = client

        if config is None:
            config = Config()
        self.config = config

        self.logger = init_logger('mastogit_bot-stream', basedir=self.config.LOGDIR)

        self.repo = Repo(path=config.GIT_REPO)



    def on_update(self, status:dict):
        status = Status(**status)
        if status.visibility in ('private', 'direct'):
            # not xposting dms
            self.logger.info('Not xposting private messages')
            return

        post = Post.from_status(status)
        if post.text.startswith('xpost'):
            self.logger.info('Not xposting an xpost')
            return

        success = self.repo.post(post.format_commit())
        if success:
            self.logger.info('Posted to git!')
        else:
            self.logger.exception('Failed to post to git!')





class Bot:
    def __init__(self, config:Optional[Config]=None, post_length=500):
        self._me = None # type: Optional[Account]
        self._me_list = None # type: Optional[List]

        if config is None:
            config = Config()

        self.config = config
        self.config.LOGDIR.mkdir(exist_ok=True)
        self.post_length = post_length
        self.logger = init_logger('mastogit_bot', basedir=self.config.LOGDIR)

        self.client = Mastodon(
            access_token=self.config.MASTO_TOKEN,
            api_base_url=self.config.MASTO_URL
        )

    def init_stream(self, run_async:bool=True):
        # Listen to a stream consisting of just us.
        listener = Listener(client=self.client, config=self.config)
        self.logger.info('Initializing streaming')
        self.client.stream_list(
            self.me_list.id,
            listener = listener,
            run_async=run_async
        )

    def post(self, post:str):
        # TODO: Split long posts
        if len(post)>self.post_length:
            raise NotImplementedError(f"Cant split long posts yet, got post of length {len(post)} when max length is {self.post_length}")

        self.client.status_post(post)
        self.logger.info(f"Posted:\n{post}")

    @property
    def me(self) -> Account:
        if self._me is None:
            self._me = Account(**self.client.me())
        return self._me

    def _make_me_list(self) -> List:
        me_list = List(**self.client.list_create('me'))
        self.client.list_accounts_add(me_list.id, [self.me.id])
        self.logger.info('Created list with just me in it!')
        return me_list

    @property
    def me_list(self) -> List:
        if self._me_list is None:
            lists = self.client.lists()
            me_list = [l for l in lists if l.get('title', '') == 'me']
            if len(me_list)>0:
                self._me_list = List(**me_list[0])
            else:
                self._me_list = self._make_me_list()
        return self._me_list
