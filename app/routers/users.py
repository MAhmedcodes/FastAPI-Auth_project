from fastapi import Depends, status, HTTPException, APIRouter

from app.utils import utils
from sqlalchemy.orm import Session

from app import models
from app import schemas
from ..database.database import get_db
from colorama import Fore

router = APIRouter( 
    tags=["USERS"]
)

#Creating a User
@router.post("/user-registration", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_pwd = utils.hashing(user.password)
    user.password = hashed_pwd

    new_user = models.Users(**user.model_dump())
    db.add(new_user)
    db.commit()
    print( Fore.BLUE + "User Created")
    db.refresh(new_user)
    return new_user

#Fetching single user
@router.get("/users/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} does not exist")
    return user
