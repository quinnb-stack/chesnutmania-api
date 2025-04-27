from fastapi import FastAPI
from app.database import MongoDatabaseSession
from .routers import user_router as users

get_db = MongoDatabaseSession("sample_users")

app = FastAPI(title="Users")

app.include_router(users.router)
