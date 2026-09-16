import uvicorn
from fastapi import FastAPI
from pathlib import Path
from api.business import router as business_router
from api.pages import router as pages_router
from api.auth import router as auth_router
from api.user import router as user_router

app = FastAPI()

app.include_router(business_router)
app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(user_router)


BASE_DIR = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    uvicorn.run("main:app", host = "0.0.0.0", port = 8000, reload = True)