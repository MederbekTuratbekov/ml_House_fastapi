from pydantic_core.core_schema import model_field
from fastapi_house.db.models import UserProfile, Property, Review
from sqladmin import ModelView


class UserProfileAdmin(ModelView, model=UserProfile):
    column_list = [UserProfile.first_name, UserProfile.last_name]

class PropertyAdmin(ModelView, model=Property):
    column_list = [Property.id, Property.property_name]

class ReviewAdmin(ModelView, model=Review):
    column_list = [Review.stars, Review.text]
