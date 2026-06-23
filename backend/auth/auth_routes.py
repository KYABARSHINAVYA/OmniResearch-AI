from fastapi import APIRouter
from pydantic import BaseModel

from auth.mongo_models import users_collection
from auth.password_utils import (
    hash_password,
    verify_password
)
from auth.jwt_auth import create_access_token


router = APIRouter()


class User(BaseModel):

    email: str

    password: str


@router.post("/signup")
def signup(user: User):

    existing_user = users_collection.find_one(
        {
            "email": user.email
        }
    )

    if existing_user:

        return {
            "message": "User already exists"
        }

    users_collection.insert_one(
        {
            "email": user.email,
            "password": hash_password(
                user.password
            )
        }
    )

    return {
        "message": "Signup successful"
    }


@router.post("/login")
def login(user: User):

    existing_user = users_collection.find_one(
        {
            "email": user.email
        }
    )

    if not existing_user:

        return {
            "message": "User not found"
        }

    if not verify_password(
            user.password,
            existing_user["password"]
    ):

        return {
            "message": "Wrong password"
        }

    token = create_access_token(
        {
            "email": user.email
        }
    )

    return {

        "access_token": token
    }
