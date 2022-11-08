from pathlib import Path
from subprocess import run
import json
from urllib.parse import urljoin

from pydantic import BaseModel, EmailStr

log_format = '{%n  "commit": "%H",%n  "abbreviated_commit": "%h",%n  "tree": "%T",%n  "abbreviated_tree": "%t",%n  "parent": "%P",%n  "abbreviated_parent": "%p",%n  "refs": "%D",%n  "encoding": "%e",%n  "subject": "%s",%n  "sanitized_subject_line": "%f",%n  "body": "%b",%n  "commit_notes": "%N",%n  "verification_flag": "%G?",%n  "signer": "%GS",%n  "signer_key": "%GK",%n  "author": {%n    "name": "%aN",%n    "email": "%aE",%n    "date": "%aD"%n  },%n  "commiter": {%n    "name": "%cN",%n    "email": "%cE",%n    "date": "%cD"%n  }%n}'
"""Thanks https://gist.github.com/varemenos/e95c2e098e657c7688fd"""

class Author(BaseModel):
    name: str
    email: EmailStr
    date: str

class Commit(BaseModel):
    commit:str
    abbreviated_commit:str
    subject:str
    body:str
    author: Author
    commiter: Author

    def make_url(self, remote_url:str):
        return urljoin(remote_url, f'commit/{self.abbreviated_commit}')

    class Config:
        extra='ignore'

class Repo:
    def __init__(self, path:Path):
        self.path = Path(path)

    @property
    def last_commit(self) -> Commit:
        path = self.path
        output = run([
            'git',
            '-C', str(path),
            'log',
            '--pretty=format:'+log_format,
            'HEAD^..HEAD'
        ],
            capture_output=True
        )
        parse = json.loads(output.stdout, strict=False)
        return Commit(**parse)