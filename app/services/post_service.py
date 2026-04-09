# app/services/post_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
from typing import List, Optional

class PostService:
    
    @staticmethod
    def get_all_posts(db: Session, current_user_id: int) -> List:
        """Get all posts with vote counts"""
        return db.query(
            models.Post,
            func.count(models.Votes.post_id).label("votes")
        ).join(
            models.Votes, models.Votes.post_id == models.Post.id, isouter=True
        ).group_by(models.Post.id).all()
    
    @staticmethod
    def get_filtered_posts(db: Session, fetch: int, skip: int, search: Optional[str]) -> List:
        """Get filtered posts"""
        query = db.query(
            models.Post,
            func.count(models.Votes.post_id).label("votes")
        ).join(
            models.Votes, models.Votes.post_id == models.Post.id, isouter=True
        ).group_by(models.Post.id)
        
        if search:
            query = query.filter(models.Post.title.contains(search))
        
        return query.limit(fetch).offset(skip).all()
    
    @staticmethod
    def get_user_posts(db: Session, user_id: int) -> List:
        """Get all posts by a specific user"""
        return db.query(
            models.Post,
            func.count(models.Votes.post_id).label("votes")
        ).join(
            models.Votes, models.Votes.post_id == models.Post.id, isouter=True
        ).filter(
            models.Post.user_id == user_id
        ).group_by(models.Post.id).all()
    
    @staticmethod
    def get_post_by_id(db: Session, post_id: int, current_user_id: int):
        """Get single post with validation"""
        post = db.query(
            models.Post,
            func.count(models.Votes.post_id).label("votes")
        ).join(
            models.Votes, models.Votes.post_id == models.Post.id, isouter=True
        ).filter(
            models.Post.id == post_id
        ).group_by(models.Post.id).first()
        
        if not post:
            return None
        
        # Check if user can view this post
        if not post.Post.published and post.Post.user_id != current_user_id:
            return None
            
        return post
    
    @staticmethod
    def create_post(db: Session, post_data: schemas.CreatePost, user_id: int):
        """Create a new post"""
        new_post = models.Post(
            user_id=user_id,
            **post_data.model_dump()
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    
    @staticmethod
    def delete_post(db: Session, post_id: int, user_id: int) -> bool:
        """Delete a post if user is owner"""
        post = db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            return False
        if post.user_id != user_id: # type: ignore
            return False
        
        db.delete(post)
        db.commit()
        return True
    
    @staticmethod
    def update_post(db: Session, post_id: int, post_data: schemas.CreatePost, user_id: int):
        """Update a post if user is owner"""
        post = db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            return None
        if post.user_id != user_id: # type: ignore
            return None
        
        for key, value in post_data.model_dump().items():
            setattr(post, key, value)
        
        db.commit()
        db.refresh(post)
        return post
    