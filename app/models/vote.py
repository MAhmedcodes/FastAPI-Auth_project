from sqlalchemy import INTEGER, ForeignKey, Column
from ..database.database import Base

class Votes(Base):
    __tablename__ = "votes"

    voter_id = Column(INTEGER, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(INTEGER, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    