from typing import Optional
from masto_git_bridge.config import Config
from masto_git_bridge.repo import Repo
from masto_git_bridge.bot import Bot
from masto_git_bridge.post import Post
from masto_git_bridge.logger import init_logger
from time import sleep

def post_last_commit(config:Optional[Config]=None):
    """
    Should be triggered as a commit hook because it doesn't validate
    the last commit hasn't already been posted.
    """
    if config is None:
        config = Config()
    logger = init_logger('post-git', basedir=config.LOGDIR)

    repo = Repo(config.GIT_REPO)
    last_commit = repo.last_commit
    post = Post.from_commit(last_commit)

    if post.text.startswith('xpost'):
        logger.info('Not xposting an xpost')
        return


    bot = Bot(config=config)
    bot.post(post.format_masto())

def masto_gitbot(config:Optional[Config]=None):
    if config is None:
        config = Config()

    bot = Bot(config=config)
    try:
        bot.init_stream()
        while True:
            sleep(60*60)
            bot.logger.info('taking a breath')
    except KeyboardInterrupt:
        bot.logger.info('quitting!')

