from .database import Base
from sqlalchemy import (ForeignKey, String, Integer, DateTime, Enum, Text, Boolean, DECIMAL)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum as PyEnum


class ROLE_CHOICES(str, PyEnum):
    admin = 'admin'
    seller = 'seller'
    buyer = 'buyer'

class UserProfile(Base):
    __tablename__ = 'userprofile'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str] = mapped_column(String(32))
    lastname: Mapped[str] = mapped_column(String(32))
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    phone_number: Mapped[str | None] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[ROLE_CHOICES] = mapped_column(Enum(ROLE_CHOICES))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda : datetime.now(timezone.utc))

    seller_property: Mapped[List['Property']] = relationship('Property', back_populates='seller', cascade='all, delete-orphan')
    seller_review: Mapped[List['Property']] = relationship('Property', back_populates='seller', cascade='all, delete-orphan')
    buyer_review: Mapped[List['Review']] = relationship('Review', back_populates='buyer', cascade='all, delete-orphan')

    def __str__(self):
        return f'{UserProfile.username} {UserProfile.role}'

class RefreshToken(Base):
    __tablename__ = 'refresh_token'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    token: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda : datetime.now(timezone.utc))

    def __str__(self):
        return f'{RefreshToken.token}'

class PROPERTY_TYPE(str, PyEnum):
    apartment = 'apartment'
    house = 'house'
    commercial_property = 'commercial_property'
    room = 'room'
    land_plot_or_lot = 'land_plot_or_lot'
    summer_house_or_country_house = 'summer_house_or_country_house'
    parking_space_or_garage = 'parking_space_or_garage'

class CHOICE_REGION(str, PyEnum):
        Chui = 'Chui'
        Talas = 'Talas'
        Jalal_Abad = 'Jalal_Abad'
        Osh = 'Osh'
        Batken = 'Batken'
        Ysyk_Kol = 'Ysyk_Kol'
        Naryn = 'Naryn'

class CHOICE_CITY(str, PyEnum):
        Bishkek = 'Bishkek'
        Talas = 'Talas'
        Jalal_Abad = 'Jalal_Abad'
        Osh = 'Osh'
        Batken = 'Batken'
        Kara_Kol = 'Kara_Kol'
        Naryn = 'Naryn'

class Property(Base):
    __tablename__ = 'property'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    property_type: Mapped[PROPERTY_TYPE] = mapped_column(Enum(PROPERTY_TYPE))
    region: Mapped[CHOICE_REGION] = mapped_column(Enum(CHOICE_REGION))
    city: Mapped[CHOICE_CITY] = mapped_column(Enum(CHOICE_CITY))
    district: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(100))
    area: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price: Mapped[int] = mapped_column(Integer, default=1)
    rooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    images: Mapped[str | None] = mapped_column(String, nullable=True) # реализовать путь сохранения
    documents: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda : datetime.now(timezone.utc))

    seller_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    seller: Mapped['UserProfile'] = relationship('UserProfile', back_populates='seller_property')

    def __str__(self):
        return f'{Property.title} {Property.city} {Property.price}'

class Review(Base):
    __tablename__ = 'review'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda : datetime.now(timezone.utc))

    buyer_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    buyer: Mapped['UserProfile'] = relationship('UserProfile', back_populates='buyer_review')
    seller_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    seller: Mapped['UserProfile'] = relationship('UserProfile', back_populates='seller_review')

    def __str__(self):
        return f'{Review.seller} {Review.rating} {Review.comment}'
