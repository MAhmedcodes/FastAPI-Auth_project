from sqlalchemy import Integer, Column, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from ..database.database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True ,nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)

    posts = relationship("Post", back_populates="owner")