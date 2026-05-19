from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from backend.utils.auth import authenticate_user, create_access_token, get_current_user
except ModuleNotFoundError:
    from utils.auth import authenticate_user, create_access_token, get_current_user

from fastapi import Depends

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(payload: LoginRequest):
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "user": user,
    }


@router.get("/me")
def me(user=Depends(get_current_user)):
    return user
