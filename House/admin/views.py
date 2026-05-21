from pydantic_core.core_schema import model_field
from db.models import UserProfile, Property, Review
from sqladmin import ModelView


class UserProfileAdmin(ModelView, model=UserProfile):
    column_list = [UserProfile.firstname, UserProfile.lastname]

class PropertyAdmin(ModelView, model=Property):
    column_list = [Property.id, Property.property_type]

class ReviewAdmin(ModelView, model=Review):
    column_list = [Review.rating, Review.comment]
