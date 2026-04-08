# app/routers/posts.py (simplified using service)
from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas
from app.core.oauth2 import oauth2
from app.database.database import get_db
from app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["POSTS"])

@router.get("/", response_model=List[schemas.VotedResponse])
def get_posts(
    db: Session = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(oauth2.current_user)
):
    """Get all posts with vote counts"""
    return PostService.get_all_posts(db, current_user.id)

@router.get("/filter", response_model=List[schemas.VotedResponse])
def get_filtered_posts(
    fetch: int = 5,
    skip: int = 2,
    search: Optional[str] = "",
    db: Session = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(oauth2.current_user)
):
    """Get filtered posts"""
    return PostService.get_filtered_posts(db, fetch, skip, search)

@router.get("/my-posts", response_model=List[schemas.VotedResponse])
def get_my_posts(
    db: Session = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(oauth2.current_user)
):
    """Get current user's posts"""
    return PostService.get_user_posts(db, current_user.id)

@router.get("/{id}", response_model=schemas.VotedResponse)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(oauth2.current_user)
):
    """Get a single post"""
    post = PostService.get_post_by_id(db, id, current_user.id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Response)
def create_post(
    post: schemas.CreatePost,
    db: Session = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(oauth2.current_user)
):
    """Create a new post"""
    return PostService.create_post(db, post, current_user.id)

@router.delete("/{id}")
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(oauth2.current_user)
):
    """Delete a post"""
    deleted = PostService.delete_post(db, id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found or unauthorized")
    return {"message": "Post deleted"}

@router.put("/{id}", response_model=schemas.Response)
def update_post(
    id: int,
    post: schemas.CreatePost,
    db: Session = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(oauth2.current_user)
):
    """Update a post"""
    updated = PostService.update_post(db, id, post, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Post not found or unauthorized")
    return updated
