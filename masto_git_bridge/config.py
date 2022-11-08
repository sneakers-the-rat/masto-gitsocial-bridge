from pathlib import Path
from pydantic import BaseSettings, AnyHttpUrl

class Config(BaseSettings):
    MASTO_URL:AnyHttpUrl
    MASTO_TOKEN:str
    GIT_REPO:Path
    GIT_REMOTE_URL:AnyHttpUrl
    LOGDIR:Path=Path().home() / '.mastogit'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_prefix = "MASTOGIT_"

