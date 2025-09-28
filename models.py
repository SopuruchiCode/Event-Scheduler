from pydantic import BaseModel
from typing import Literal
from datetime import datetime, time

Role = Literal["user", "admin"]


class user_model(BaseModel):
    username: str
    email: str
    # profile_pic: str | None = None
    password: str   #should be hashed
    date_created: datetime | None = None
    role: Role = "user"
    is_active: bool = True
    

class event_model(BaseModel):
    name: str 
    creator_id : str | None = None
    location: str
    date: datetime
    time: time
    duration: int
    capacity: int