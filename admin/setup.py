from .views import UserProfileAdmin, PropertyAdmin, ReviewAdmin
from fastapi import FastAPI
from sqladmin import Admin
from fastapi_house.db.database import engine


def setup_admin(udemy:FastAPI):
    admin = Admin(udemy, engine)
    admin.add_view(UserProfileAdmin)
    admin.add_view(PropertyAdmin)
    admin.add_view(ReviewAdmin)
