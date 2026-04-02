from re import I

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, Integer, Column, String, text
from sqlalchemy.orm import relationship
from ..database.database import Base

class Post(Base):

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='True')
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)
    user_id = Column(Integer,ForeignKey("users.id", ondelete="CASCADE"),nullable=False)

    owner = relationship("Users", back_populates="posts")