from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel
import re
from bs4 import BeautifulSoup

from masto_git_bridge.repo import Commit
from masto_git_bridge.models import Account

class Status(BaseModel):
    """
    Model of a toot on mastodon

    See: https://mastodonpy.readthedocs.io/en/stable/#toot-dicts
    """
    id: int
    url: str
    account: Account
    content: str
    visibility: Literal['public', 'unlisted', 'private', 'direct']
    in_reply_to_id: Optional[int] = None
    in_reply_to_account_id: Optional[int] = None

    class Config:
        extra='ignore'

class Post(BaseModel):
    #timestamp: Optional[datetime] = None
    text:str
    status:Optional[Status] = None
    commit:Optional[Commit] = None

    @classmethod
    def from_commit(cls, commit:Commit) -> 'Post':
        text = '\n'.join([commit.subject, commit.body])
        return Post(text=text, commit=commit)

    @classmethod
    def from_status(cls, status:Status) -> 'Post':
        # split paragraphs using bs4
        soup = BeautifulSoup(status.content, 'lxml')
        # replace with double line breaks
        pars = [p.text for p in soup.find_all('p')]
        text = '\n\n'.join(pars)
        return Post(text=text, status=status)

    def format_masto(self) -> str:
        """
        Format a post to go from git -> masto.

        Needs to have a :attr:`.commit` attribute!

        Does not split the body text into multiple toots.
        That should be handled in the posting action

        Example:

            git-social: https://{repo_url}/commits/{hash}
            {subject line}
            {body}
        """
        return f"xpost from git-social: {self.commit.url}\n---\n{self.text}"""

    def format_commit(self) -> str:
        """
        Add a link back to original masto post split by double lines
        """
        return f"xpost from mastodon: {self.status.url}\n\n{self.text}"