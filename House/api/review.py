from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from jose import jwt, JWTError
from db.database import get_db
from db.models import Review, UserProfile, ROLE_CHOICES
from db.schema import ReviewSchema, ReviewCreateSchema
from config import SECRET_KEY, ALGORITHM

review_router = APIRouter(prefix='/review', tags=['Review'])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Недействительный токен")
        user = db.query(UserProfile).filter(UserProfile.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токен")

@review_router.post('/', response_model=ReviewSchema)
async def review_create(review: ReviewCreateSchema, seller_id: int, user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != ROLE_CHOICES.buyer:
        raise HTTPException(status_code=403, detail="Только покупатели могут оставлять отзывы")
    seller = db.query(UserProfile).filter(UserProfile.id == seller_id).first()
    if not seller or seller.role != ROLE_CHOICES.seller:
        raise HTTPException(status_code=404, detail="Продавец не найден")
    db_review = Review(**review.dict(), buyer_id=user.id, seller_id=seller_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@review_router.get('/', response_model=List[ReviewSchema])
async def review_list(db: Session = Depends(get_db)):
    return db.query(Review).all()

@review_router.get('/{review_id}', response_model=ReviewSchema)
async def review_detail(review_id: int, db: Session = Depends(get_db)):
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    return db_review

@review_router.post('/{review_id}', response_model=dict)
async def review_update(review_id: int, review: ReviewCreateSchema, user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    if db_review.buyer_id != user.id:
        raise HTTPException(status_code=403, detail="Можно редактировать только свои отзывы")
    for key, value in review.dict().items():
        setattr(db_review, key, value)
    db.commit()
    db.refresh(db_review)
    return {"message": "Обновлено"}

@review_router.delete('/{review_id}', response_model=dict)
async def review_delete(review_id: int, user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    if db_review.buyer_id != user.id:
        raise HTTPException(status_code=403, detail="Можно удалять только свои отзывы")
    db.delete(db_review)
    db.commit()
    return {"message": "Удалено"}