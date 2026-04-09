from pydantic import BaseModel, conint
from typing import Annotated

class Votes(BaseModel):

    post_id: int
    direction: Annotated[int, conint(ge=0, le=1)]
    