from pydantic import BaseModel
from typing import Optional

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[str] = None
    type: Optional[str] = None
    poster: Optional[str] = None