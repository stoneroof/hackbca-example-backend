from datetime import datetime
from pydantic import BaseModel
from typing import List, Literal, Optional
from uuid import UUID


class UserIn(BaseModel):
    email: str


class UserOut(UserIn):
    id: UUID


class User(UserOut):
    google_subject: Optional[str]

    class Config:
        orm_mode = True


class LoginTokenIn(BaseModel):
    id: UUID


class LoginToken(LoginTokenIn):
    user: UserOut

    class Config:
        orm_mode = True


class ProjectIn(BaseModel):
    name: str
    users: List[UUID]
    date_proposed: datetime
    time: datetime
    type: Literal["software", "hardware"]
    description: Optional[str]
    github: Optional[str]
    url: Optional[str]


class Project(ProjectIn):
    id: UUID
    users: List[UserOut]

    class Config:
        orm_mode = True
