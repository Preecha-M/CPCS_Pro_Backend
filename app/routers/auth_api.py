from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from datetime import datetime

from ..core.mongo import col_users
from ..core.auth import (
    create_access_token,
    get_current_user_from_cookie,
    set_auth_cookie,
    clear_auth_cookie,
)
from ..core.password_hasher import (
    verify_password,
    hash_password_argon2,
    needs_upgrade_to_argon2,
)

router = APIRouter()


class LoginBody(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=200)


class RegisterBody(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=200)
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=6, max_length=30)
    affiliation: str = Field(min_length=1, max_length=120)
    role: Literal["admin", "researcher"]


def _public_user(u: dict) -> dict:
    return {
        "id": str(u.get("_id")),
        "username": u.get("username"),
        "role": u.get("role"),
        "name": u.get("name", ""),
        "email": u.get("email", ""),
        "phone": u.get("phone", ""),
        "affiliation": u.get("affiliation", ""),
    }


@router.get("/auth/me")
async def me(request: Request):
    payload = get_current_user_from_cookie(request)
    user = col_users.find_one({"username": payload.get("username")})
    if not user:
        return JSONResponse({"detail": "User not found"}, status_code=401)
    return _public_user(user)


@router.post("/auth/login")
async def login(body: LoginBody):
    user = col_users.find_one({"username": body.username})
    if not user or not verify_password(body.password, user.get("password_hash", "")):
        return JSONResponse({"detail": "Invalid username or password"}, status_code=401)

    old_hash = user.get("password_hash", "")
    if needs_upgrade_to_argon2(old_hash):
        new_hash = hash_password_argon2(body.password)
        col_users.update_one({"_id": user["_id"]}, {"$set": {"password_hash": new_hash}})
        user["password_hash"] = new_hash

    token = create_access_token({"username": user["username"], "role": user.get("role", "researcher")})
    res = JSONResponse(_public_user(user))
    set_auth_cookie(res, token)
    return res


@router.post("/auth/logout")
async def logout():
    res = JSONResponse({"ok": True})
    clear_auth_cookie(res)
    return res


@router.post("/auth/register")
async def register(request: Request, body: RegisterBody):
    payload = get_current_user_from_cookie(request)
    if payload.get("role") != "admin":
        return JSONResponse({"detail": "Admin only"}, status_code=403)

    exists = col_users.find_one({"username": body.username})
    if exists:
        return JSONResponse({"detail": "Username already exists"}, status_code=400)

    doc = {
        "username": body.username,
        "password_hash": hash_password_argon2(body.password),
        "name": body.name,
        "email": str(body.email),
        "phone": body.phone,
        "affiliation": body.affiliation,
        "role": body.role,
        "created_at": datetime.utcnow(),
    }

    col_users.insert_one(doc)
    return {"ok": True}
