from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from .models import ROLE_CHOICES, PROPERTY_TYPE, CHOICE_REGION, CHOICE_CITY


class UserProfileLoginSchema(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True

class UserProfileRegisterSchema(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: EmailStr
    phone_number: Optional[str] = None
    password: str
    role: ROLE_CHOICES

    class Config:
        from_attributes = True

class UserProfileSchema(BaseModel):
    id: int
    avatar: str | None
    first_name: str
    lastname: str
    username: str
    email: EmailStr
    phone_number: Optional[str] = None
    password: str
    role: ROLE_CHOICES
    created_date: datetime

    class Config:
        from_attributes = True

class PropertyCreateSchema(BaseModel):
    title: str
    description: str
    property_type: PROPERTY_TYPE
    region: CHOICE_REGION
    city: CHOICE_CITY
    district: str
    address: str
    area: Optional[int] = Field(None, ge=0, le=10000)  # Площадь не меньше 0
    price: Optional[int] = Field(None, gt=0, le=99999999)  # Цена строго положительная
    rooms: Optional[int] = Field(None, ge=1, le=50)  # Количество комнат не меньше 1
    images: Optional[str] = None
    documents: bool

    class Config:
        from_attributes = True

class PropertySchema(BaseModel):
    id: int
    title: str
    description: str
    property_type: PROPERTY_TYPE
    region: CHOICE_REGION
    city: CHOICE_CITY
    district: str
    address: str
    area: int | None
    price: Optional[int] | None
    rooms: Optional[int] = None
    images:str | None
    documents: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewSchema(BaseModel):
    id: int
    comment: str | None
    rating: int | None
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewCreateSchema(BaseModel):
    comment: str | None
    rating: Optional[int] = Field(None, ge=1, le=5)

    class Config:
        from_attributes = True
