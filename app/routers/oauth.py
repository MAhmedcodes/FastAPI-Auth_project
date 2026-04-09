from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.oauth.oauth import oauth
from app.core.oauth2.oauth2 import create_access_token
from app.core.config.config import settings
from app import models, schemas

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/google/login")
async def google_login(request: Request):
    """Redirect to Google login"""
    # Make sure this matches what you set in Google Cloud Console
    redirect_uri = settings.google_redirect_uri
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback", response_model= schemas.OAuthResponse)
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google callback and return JWT token"""
    try:
        # Get user info from Google
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            # Try alternative way to get user info
            resp = await oauth.google.get('userinfo', token=token)
            user_info = resp.json()
        
        email = user_info.get('email')
        google_id = str(user_info.get('sub'))
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        # Find or create user
        user = db.query(models.Users).filter(
            models.Users.oauth_provider == 'google',
            models.Users.oauth_id == google_id
        ).first()
        
        if not user:
            # Check if user exists with same email
            user = db.query(models.Users).filter(
                models.Users.email == email
            ).first()
            
            if user:
                # Update existing user with OAuth info
                user.oauth_provider = 'google' # type: ignore
                user.oauth_id = google_id # type: ignore
                db.commit()
                db.refresh(user)
            else:
                # Create new user
                user = models.Users(
                    email=email,
                    password=None,
                    oauth_provider='google',
                    oauth_id=google_id
                )
                db.add(user)
                db.commit()
                db.refresh(user)
        
        # Create JWT token
        jwt_token = create_access_token(data={"id": user.id})
        
        return schemas.OAuthResponse(
            access_token=jwt_token,
            token_type="bearer",
            user_id=user.id, # type: ignore
            email=user.email, # type: ignore
            message="Google login successful"
        )
        
    except Exception as e:
        print(f"Google login error: {str(e)}")  # For debugging
        raise HTTPException(status_code=400, detail=f"Google login failed: {str(e)}")

@router.get("/github/login")
async def github_login(request: Request):
    """Redirect to GitHub login"""
    redirect_uri = settings.github_redirect_uri
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/github/callback", response_model=schemas.OAuthResponse)
async def github_callback(request: Request, db: Session = Depends(get_db)):
    """Handle GitHub callback and return JWT token"""
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
        
        # Find or create user
        user = db.query(models.Users).filter(
            models.Users.oauth_provider == 'github',
            models.Users.oauth_id == github_id
        ).first()
        
        if not user:
            # Check if user exists with same email
            user = db.query(models.Users).filter(
                models.Users.email == email
            ).first()
            
            if user:
                # Update existing user with OAuth info
                user.oauth_provider = 'github' # type: ignore
                user.oauth_id = github_id # type: ignore
                db.commit()
                db.refresh(user)
            else:
                # Create new user
                user = models.Users(
                    email=email,
                    password=None,
                    oauth_provider='github',
                    oauth_id=github_id
                )
                db.add(user)
                db.commit()
                db.refresh(user)
        
        # Create JWT token
        jwt_token = create_access_token(data={"id": user.id})
        
        return schemas.OAuthResponse(
            access_token=jwt_token,
            token_type="bearer",
            user_id=user.id, # type: ignore
            email=user.email, # type: ignore
            message="GitHub login successful"
        )
        
    except Exception as e:
        print(f"github login error: {str(e)}")  # For debugging
        raise HTTPException(status_code=400, detail=f"github login failed: {str(e)}")
    