from fastapi import Depends, status, HTTPException, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app import models
from app import schemas
from app.core.oauth2 import oauth2
from app.utils import utils

router = APIRouter(
    prefix="/users",
    tags=["Authentication"]
)

@router.post("/login", response_model=schemas.Token)

def login(
    cred: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(models.Users).filter(
        models.Users.email == cred.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Email or Password"
        )

    if not utils.verify(cred.password, user.password):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Email or Password"
        )

    access_token = oauth2.create_access_token(
        data={"id": user.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }