from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Post(BaseModel):
    timestamp: datetime
    hash: Optional[str]
