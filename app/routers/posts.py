from ast import Mod

from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from typing import List, Optional
from colorama import Fore

from app import models
from app.core.oauth2 import oauth2
from app import models
from app import schemas
from ..database.database import get_db

router = APIRouter(
    prefix= "/posts",
    tags=["POSTS"]
)

#Posts functions
#Read
@router.get("/", response_model=List[schemas.VotedResponse])
def get_post(db: Session = Depends(get_db), get_current_user: schemas.CurrentUser = Depends(oauth2.current_user)):
    # posts = db.query(models.Post).filter(or_( models.Post.user_id == get_current_user.id, models.Post.published == True)).all()
    get_votes_query = db.query(
        models.Post, func.count(
            models.Votes.post_id).label(
                "votes")).join(
                    models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(
                        models.Post.id).all()

    return get_votes_query

#filtered
@router.get("/filter", response_model=List[schemas.VotedResponse])
def get_filtered_post(db: Session = Depends(get_db), get_current_user: schemas.CurrentUser = Depends(oauth2.current_user),
             fetch: int = 5, skip: int = 2, search: Optional[str] = ""):
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(fetch).offset(skip).all()
    posts = db.query(
        models.Post, func.count(
            models.Votes.post_id).label("votes")).join(
                models.Votes, models.Votes.post_id == models.Post.id, isouter=True).filter(
                    models.Post.title.contains(search)).group_by(
                        models.Post.id).limit(fetch).offset(skip).all()
    
    return posts

# get single user all posts

@router.get("/all", response_model=List[schemas.VotedResponse])
def get_all_by_single_user(db: Session = Depends(get_db), get_current_user: schemas.CurrentUser = Depends(oauth2.current_user)):
    # posts = db.query(models.Post).filter(models.Post.user_id == get_current_user.id).all()
    posts = db.query(
        models.Post, func.count(
            models.Votes.post_id).label("votes")).join(
                models.Votes, models.Votes.post_id == models.Post.id, isouter=True).filter(
                    models.Post.user_id == get_current_user.id
                         ).group_by(models.Post.id).all()
    return posts

#read single
@router.get("/{id}", response_model=schemas.VotedResponse)
def get_single_post(
    id:int,
    db: Session = Depends(get_db),
    get_current_user: schemas.CurrentUser = Depends(oauth2.current_user)
):

    single = db.query(
        models.Post,
        func.count(models.Votes.post_id).label("votes")
    ).join(
        models.Votes,
        models.Votes.post_id == models.Post.id,
        isouter=True
    ).filter(
        models.Post.id == id
    ).group_by(
        models.Post.id
    ).first()

    if not single:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    if (
        single.Post.published is False and
        single.Post.user_id != get_current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    return single    


#Create
@router.post("/", status_code= status.HTTP_201_CREATED, response_model=schemas.Response)
def create_post(post : schemas.CreatePost, db: Session = Depends(get_db), get_current_user: schemas.CurrentUser = Depends(oauth2.current_user)):
    print(get_current_user)
    new_post = models.Post(user_id = get_current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    print ( Fore.BLUE + "Post Created")
    return new_post

#delete
@router.delete("/{id}")
def delete_post(id :int,db: Session = Depends(get_db), get_current_user: schemas.CurrentUser = Depends(oauth2.current_user)):
    deleted_query = db.query(models.Post).filter(models.Post.id == id)
    deleted_post = deleted_query.first()
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id = {id} not found"
                            )
    if (deleted_post.user_id != get_current_user.id):  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Forbidden! You are not the owner of post")
    deleted_query.delete(synchronize_session=False)
    db.commit()
    return {"message": "Post is deleted"}

#update
@router.put("/{id}", response_model=schemas.Response)
def update_post(id : int, post : schemas.CreatePost, db: Session = Depends(get_db), get_current_user: schemas.CurrentUser = Depends(oauth2.current_user)):
    update_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = update_query.first()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id = {id} not found")
    if (updated_post.user_id != get_current_user.id):  # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Forbidden! You are not the owner of post")
    update_query.update(post.model_dump(), synchronize_session=False) # type: ignore
    db.commit()
    db.refresh(updated_post)
    return updated_post
