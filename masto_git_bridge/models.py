from pydantic import BaseModel

class Account(BaseModel):
    """Not transcribing full model now, just using to check"""
    acct: str
    id: int

    class Config:
        extra = 'ignore'