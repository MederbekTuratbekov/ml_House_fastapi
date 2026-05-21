from fastapi import APIRouter, Depends
from db.database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth
from config import settings


social_router = APIRouter(prefix='/oauth', tags=['Social Auth'])

# github -------------------------------------------------------

oauth = OAuth()
oauth.register(
    name='github',
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_KEY,
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    api_base_url='https://api.github.com/'
)

@social_router.get('/github/callback')
async def github_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.github.authorize_access_token(request)
    user_info = await oauth.github.get('user', token=token)
    return {"message": "GitHub login successful"}
# google -------------------------------------------------------

oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_KEY,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    client_kwargs={"scope": "openid profile email"},
    userinfo_endpoint='https://www.googleapis.com/oauth2/v3/userinfo'
)

@social_router.get('/google/callback')
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.get('userinfo', token=token)
    return {"message": "Google login successful"}