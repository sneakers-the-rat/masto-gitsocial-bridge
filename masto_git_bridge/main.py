from typing import Optional
from masto_git_bridge.config import Config
from masto_git_bridge.repo import Repo

def post_last_commit(config:Optional[Config]=None):
    if config is None:
        config = Config()

    repo = Repo(config.GIT_REPO)
    last_commit = repo.last_commit
