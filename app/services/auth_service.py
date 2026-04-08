# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models
from app.utils import utils
from app.core.oauth2 import oauth2

class AuthService:
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        """Authenticate user with email and password"""
        user = db.query(models.Users).filter(
            models.Users.email == email
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid Email or Password"
            )
        
        if not utils.verify(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Email or Password"
            )
        
        return user
    
    @staticmethod
    def create_access_token_for_user(user_id: int):
        """Create access token for user"""
        return oauth2.create_access_token(data={"id": user_id})
    
    @staticmethod
    def handle_google_oauth(db: Session, user_info: dict):
        """Handle Google OAuth login/registration"""
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
                user.oauth_id = google_id  # type: ignore
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
        
        return user
    
    @staticmethod
    def handle_github_oauth(db: Session, user_info: dict, github_id: str, email: str):
        """Handle GitHub OAuth login/registration"""
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
        
        return user
    