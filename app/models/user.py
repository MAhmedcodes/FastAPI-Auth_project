from sqlalchemy import Integer, Column, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from ..database.database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True ,nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)
    # Just 2 new fields for OAuth
    oauth_provider = Column(String, nullable=True)  # 'google' or 'github'
    oauth_id = Column(String, nullable=True)  # ID from Google/GitHub

    posts = relationship("Post", back_populates="owner")
    