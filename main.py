from fastapi import FastAPI
import uvicorn
from api import property, review, auth, social_auth
from admin.setup import setup_admin
from starlette.middleware.sessions import SessionMiddleware
from config import SECRET_KEY


fastapi_house = FastAPI()
fastapi_house.include_router(property.property_router)
fastapi_house.include_router(review.review_router)
fastapi_house.include_router(auth.auth_router)
fastapi_house.include_router(social_auth.social_router)
fastapi_house.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
setup_admin(fastapi_house)


if __name__ == '__main__':
    uvicorn.run(fastapi_house, host='127.0.0.1', port=8001)
