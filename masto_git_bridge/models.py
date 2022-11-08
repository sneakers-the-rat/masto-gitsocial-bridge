from pydantic import BaseModel

class List(BaseModel):
    """A mastodon list!"""
    id: str
    title: str

    class Config:
        extra = 'ignore'

class Account(BaseModel):
    """Not transcribing full model now, just using to check"""
    acct: str
    id: int

    class Config:
        extra = 'ignore'