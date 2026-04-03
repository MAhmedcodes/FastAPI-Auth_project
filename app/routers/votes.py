from fastapi import Depends, status, HTTPException, APIRouter

from app.core.oauth2 import oauth2
from sqlalchemy.orm import Session

from app.database import database
from app import models
from app import schemas
from ..database.database import get_db

router = APIRouter(
    prefix="/votes",
    tags=["Votes"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def votes(vote: schemas.Votes, db: Session = Depends(database.get_db), get_current_user: schemas.CurrentUser = Depends(oauth2.current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    vote_query = db.query(models.Votes).filter(models.Votes.post_id == vote.post_id, models.Votes.voter_id == get_current_user.id)
    found_post = vote_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Post does not exist")
    if (vote.direction == 1):
        if found_post:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail="You Have already Voted for this post")
        new_vote = post.Votes(post_id = vote.post_id, voter_id = get_current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully Voted"}
    else:
        if not found_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Either Post or Vote does not exist")
        vote_query.delete()
        db.commit()
        return {"message": "Vote removed successfully"}