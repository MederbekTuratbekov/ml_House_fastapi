from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from jose import jwt, JWTError
from db.database import get_db
from db.models import Property, UserProfile, ROLE_CHOICES
from db.schema import PropertySchema, PropertyCreateSchema
from config import SECRET_KEY, ALGORITHM


property_router = APIRouter(prefix='/property', tags=['Property'])

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

@property_router.post('/', response_model=PropertySchema)
async def property_create(property: PropertyCreateSchema = Depends(), user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != ROLE_CHOICES.seller:
        raise HTTPException(status_code=403, detail="Только продавцы могут создавать объявления")
    db_property = Property(**property.dict(), seller_id=user.id)
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

@property_router.get('/', response_model=List[PropertySchema])
async def property_list(db: Session = Depends(get_db)):
    return db.query(Property).all()

@property_router.get('/{property_id}', response_model=PropertySchema)
async def property_detail(property_id: int, db: Session = Depends(get_db)):
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if db_property is None:
        raise HTTPException(status_code=404, detail="Объект недвижимости не найден")
    return db_property

@property_router.post('/{property_id}', response_model=dict)
async def property_update(property_id: int, property: PropertyCreateSchema = Depends(), user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if db_property is None:
        raise HTTPException(status_code=404, detail="Объект недвижимости не найден")
    if db_property.seller_id != user.id:
        raise HTTPException(status_code=403, detail="Можно редактировать только свои объявления")
    for key, value in property.dict().items():
        setattr(db_property, key, value)
    db.commit()
    db.refresh(db_property)
    return {"message": "Обновлено"}

@property_router.delete('/{property_id}', response_model=dict)
async def property_delete(property_id: int, user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if db_property is None:
        raise HTTPException(status_code=404, detail="Объект недвижимости не найден")
    if db_property.seller_id != user.id:
        raise HTTPException(status_code=403, detail="Можно удалять только свои объявления")
    db.delete(db_property)
    db.commit()
    return {"message": "Удалено"}
