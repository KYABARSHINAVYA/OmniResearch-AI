import hashlib
import os
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth.mongo_models import db, users_collection
from auth.password_utils import (
    hash_password,
    verify_password
)
from auth.jwt_auth import create_access_token


router = APIRouter()
otp_collection = db["auth_otps"]

OTP_EXPIRY_MINUTES = 10


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def make_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def send_email_otp(email: str, otp: str, purpose: str) -> bool:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM") or smtp_user

    if not smtp_host or not smtp_user or not smtp_password or not smtp_from:
        return False

    message = EmailMessage()
    message["Subject"] = f"OmniResearch {purpose} OTP"
    message["From"] = smtp_from
    message["To"] = email
    message.set_content(
        f"Your OmniResearch {purpose.lower()} OTP is {otp}.\n\n"
        f"This code expires in {OTP_EXPIRY_MINUTES} minutes."
    )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(message)

    return True


def save_otp(email: str, purpose: str, otp: str, password: str | None = None):
    document = {
        "email": email,
        "purpose": purpose,
        "otp_hash": hash_otp(otp),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES),
        "created_at": datetime.now(timezone.utc),
    }

    if password:
        document["password"] = hash_password(password)

    otp_collection.delete_many({"email": email, "purpose": purpose})
    otp_collection.insert_one(document)


def verify_saved_otp(email: str, purpose: str, otp: str):
    record = otp_collection.find_one({"email": email, "purpose": purpose})

    if not record:
        raise HTTPException(status_code=400, detail="OTP not found. Please request a new code.")

    expires_at = record["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        otp_collection.delete_one({"_id": record["_id"]})
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new code.")

    if record["otp_hash"] != hash_otp(otp):
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    return record


class User(BaseModel):

    email: str

    password: str


class SignupOtpRequest(User):
    pass


class VerifySignupRequest(BaseModel):

    email: str

    otp: str


class ForgotPasswordRequest(BaseModel):

    email: str


class ResetPasswordRequest(BaseModel):

    email: str

    otp: str

    password: str


@router.post("/signup")
def signup(user: User):
    email = normalize_email(user.email)

    existing_user = users_collection.find_one(
        {
            "email": email
        }
    )

    if existing_user:

        return {
            "message": "User already exists"
        }

    users_collection.insert_one(
        {
            "email": email,
            "password": hash_password(
                user.password
            ),
            "email_verified": False,
            "created_at": datetime.now(timezone.utc),
        }
    )

    return {
        "message": "Signup successful"
    }


@router.post("/signup/request-otp")
def request_signup_otp(user: SignupOtpRequest):
    email = normalize_email(user.email)

    existing_user = users_collection.find_one(
        {
            "email": email
        }
    )

    if existing_user:

        return {
            "message": "User already exists"
        }

    otp = make_otp()
    save_otp(email, "signup", otp, user.password)
    email_sent = send_email_otp(email, otp, "Signup verification")

    return {
        "message": "OTP sent to your email" if email_sent else "OTP generated. Configure SMTP to send email.",
        "dev_otp": None if email_sent else otp
    }


@router.post("/signup/verify")
def verify_signup(data: VerifySignupRequest):
    email = normalize_email(data.email)
    record = verify_saved_otp(email, "signup", data.otp)

    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        otp_collection.delete_one({"_id": record["_id"]})
        return {"message": "User already exists"}

    users_collection.insert_one(
        {
            "email": email,
            "password": record["password"],
            "email_verified": True,
            "created_at": datetime.now(timezone.utc),
        }
    )
    otp_collection.delete_one({"_id": record["_id"]})

    return {
        "message": "Signup successful"
    }


@router.post("/login")
def login(user: User):
    email = normalize_email(user.email)

    existing_user = users_collection.find_one(
        {
            "email": email
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
            "email": email
        }
    )

    return {

        "access_token": token
    }


@router.post("/forgot-password/request-otp")
def request_forgot_password_otp(data: ForgotPasswordRequest):
    email = normalize_email(data.email)
    existing_user = users_collection.find_one({"email": email})

    if not existing_user:
        return {"message": "User not found"}

    otp = make_otp()
    save_otp(email, "forgot_password", otp)
    email_sent = send_email_otp(email, otp, "Password reset")

    return {
        "message": "OTP sent to your email" if email_sent else "OTP generated. Configure SMTP to send email.",
        "dev_otp": None if email_sent else otp
    }


@router.post("/forgot-password/reset")
def reset_password(data: ResetPasswordRequest):
    email = normalize_email(data.email)
    record = verify_saved_otp(email, "forgot_password", data.otp)

    result = users_collection.update_one(
        {"email": email},
        {
            "$set": {
                "password": hash_password(data.password),
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=400, detail="User not found")

    otp_collection.delete_one({"_id": record["_id"]})

    return {"message": "Password reset successful"}
