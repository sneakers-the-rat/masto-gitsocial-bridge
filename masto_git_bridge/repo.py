import pdb
from pathlib import Path
from subprocess import run
import json
from urllib.parse import urljoin

from pydantic import BaseModel, EmailStr, AnyHttpUrl

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
    origin_url: AnyHttpUrl

    @property
    def url(self) -> str:
        return urljoin(self.origin_url + '/', f'commit/{self.abbreviated_commit}')

    class Config:
        extra='ignore'

class Repo:
    def __init__(self, path:Path):
        self.path = Path(path)

    def post(self, post:str) -> bool:
        # make paragraphs by splitting \n\n
        paras = []
        for para in post.split('\n\n'):
            paras.extend(('-m', para))

        path = self.path
        command = [
            'git',
            '-C', str(path),
            'commit',
            *paras,
            '--allow-empty'
        ]
        output = run(command, capture_output=True)
        if output.returncode != 0:
            return False

        output = run([
            'git',
            '-C', str(path),
            'push'
        ], capture_output=True)
        return True



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
        return Commit(origin_url=self.origin_url, **parse)

    @property
    def origin_url(self) -> str:
        path = self.path
        output = run([
            "git",
            '-C', str(path),
            'remote',
            'get-url',
            'origin'
        ], capture_output=True)
        url = output.stdout.decode('utf-8').strip().rstrip('.git')
        return url
