from fastapi import Depends, HTTPException, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from db.database import get_db
from db.schema import UserProfileSchema, UserProfileRegisterSchema, UserProfileLoginSchema
from db.models import UserProfile, RefreshToken
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from config import SECRET_KEY, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, ACCESS_TOKEN_EXPIRE_MINUTES


auth_router = APIRouter(prefix='/auth', tags=['Auth'])

# register -----------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

@auth_router.post('/register', response_model=dict)
async def register(user:UserProfileRegisterSchema = Depends(), db:Session=Depends(get_db)):
    check_username_email = db.query(UserProfile).filter((UserProfile.username==user.username) | (UserProfile.email==user.email)).first()
    if check_username_email is not None:
        raise HTTPException(status_code=404, detail='Почта или юзернейм уже регистрирован')
    hash_pass = get_password_hash(user.password)
    db_user = UserProfile(
        firstname=user.firstname,
        lastname=user.lastname,
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        password=hash_pass,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {'message':'Created Account'}

# login -----------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode =  data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({'exp': expire})
    return jwt.encode( to_encode, SECRET_KEY, algorithm=ALGORITHM)
def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

@auth_router.post('/login')
async def login(form_data:UserProfileLoginSchema = Depends(), db:Session=Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.username==form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=404, detail='Юзернейм же пароль туура эмес')
    access_token = create_access_token({'sub':user.username})
    refresh_token = create_refresh_token({'sub':user.username})
    new_token = RefreshToken(user_id=user.id, token=refresh_token)
    db.add(new_token)
    db.commit()
    return {'access_token':access_token, 'refresh_token':refresh_token, 'token_type':'bearer'}

# logout -----------------------------------------------------------

@auth_router.post('/logout')
async def logout(refresh_token:str, db:Session=Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail="Маалымат туура эмес")
    db.delete(stored_token)
    db.commit()
    return {'message':'Вышли'}

# refresh -----------------------------------------------------------

@auth_router.post('/refresh')
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail="Недействительный refresh-токен")
    if stored_token.created_at + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS) < datetime.now(timezone.utc):
        db.delete(stored_token)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh-токен истек")
    access_token = create_access_token({"sub": stored_token.user_id})
    return {'access_token': access_token, 'token_type': 'bearer'}
