from datetime import datetime
from pydantic import BaseModel
from .user import UserOut


class PostBase(BaseModel):

    title: str
    content: str
    published: bool = True

class CreatePost(PostBase):
    pass

class Response(PostBase):

    id: int
    created_at: datetime
    user_id: int

    owner: UserOut

    class Config:
        from_attributes = True

class VotedResponse(BaseModel):

    Post: Response
    votes: int

    class Config:
        from_attributes = True