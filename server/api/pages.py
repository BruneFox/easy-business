from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path
router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

@router.get("/")
async def start_page():
    file_path = BASE_DIR / "client" / "register.html"
    return FileResponse(file_path)

@router.get("/profile")
async def profile_page():
    file_path = BASE_DIR / "client" / "profile.html"
    return FileResponse(file_path)

@router.get("/login_page")
async def serve_login_page():
    file_path = BASE_DIR / "client" / "login.html"
    return FileResponse(file_path)

@router.get("/user_list")
async def serve_users_page():
    file_path = BASE_DIR / "client" / "users.html"
    return FileResponse(file_path)