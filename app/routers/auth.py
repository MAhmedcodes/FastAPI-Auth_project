from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app import schemas
from app.core.oauth.oauth import oauth
from app.core.config.config import settings
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=schemas.Token)
def login(
    cred: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Authenticate user
    user = AuthService.authenticate_user(db, cred.username, cred.password)
    
    # Create access token
    access_token = AuthService.create_access_token_for_user(user.id) # type: ignore
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


####### Google OAuth
@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = settings.google_redirect_uri
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback", response_model=schemas.OAuthResponse)
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        # Get user info from Google
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            # Try alternative way to get user info
            resp = await oauth.google.get('userinfo', token=token)
            user_info = resp.json()
        
        # Handle OAuth business logic
        user = AuthService.handle_google_oauth(db, user_info)
        
        # Create JWT token
        jwt_token = AuthService.create_access_token_for_user(user.id)  # type: ignore
        
        return schemas.OAuthResponse(
            access_token=jwt_token,
            token_type="bearer",
            user_id=user.id,  # type: ignore
            email=user.email,  # type: ignore
            message="Google login successful"
        )
        
    except Exception as e:
        print(f"Google login error: {str(e)}")  # For debugging
        raise HTTPException(status_code=400, detail=f"Google login failed: {str(e)}")
    
######### GitHub OAuth
@router.get("/github/login")
async def github_login(request: Request):
    redirect_uri = settings.github_redirect_uri
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/github/callback", response_model=schemas.OAuthResponse)
async def github_callback(request: Request, db: Session = Depends(get_db)):
    try:
        # Get access token
        token = await oauth.github.authorize_access_token(request)
        
        # Get user info from GitHub
        resp = await oauth.github.get('user', token=token)
        user_info = resp.json()
        
        # Get email
        email = user_info.get('email')
        if not email:
            # Get emails from GitHub
            resp_emails = await oauth.github.get('user/emails', token=token)
            emails = resp_emails.json()
            for e in emails:
                if e.get('primary') and e.get('verified'):
                    email = e.get('email')
                    break
        
        github_id = str(user_info.get('id'))
        
        if not email:
            raise HTTPException(status_code=400, detail="Could not get email from GitHub")
        
        # Handle OAuth business logic
        user = AuthService.handle_github_oauth(db, user_info, github_id, email)
        
        # Create JWT token
        jwt_token = AuthService.create_access_token_for_user(user.id)  # type: ignore
        
        return schemas.OAuthResponse(
            access_token=jwt_token,
            token_type="bearer",
            user_id=user.id,  # type: ignore
            email=user.email,  # type: ignore
            message="GitHub login successful"
        )
        
    except Exception as e:
        print(f"github login error: {str(e)}")  # For debugging
        raise HTTPException(status_code=400, detail=f"github login failed: {str(e)}")
    