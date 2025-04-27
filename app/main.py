from fastapi import FastAPI
from app.database import MongoDatabaseSession
from app.users import users

get_db = MongoDatabaseSession("sample_users")

app = FastAPI()

app.mount("/users", users.app)


@app.get("/")
def read_root():
    return {"Hello": "World"}
