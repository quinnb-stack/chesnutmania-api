from fastapi import FastAPI
from app.database import MongoDatabaseSession
from app.users import users
from app.oauth import oauth

get_db = MongoDatabaseSession("sample_users")

app = FastAPI()

app.mount("/users", users.app)
app.mount("/oauth", oauth.app)


@app.get("/")
def read_root():
    return {"I kiss na gad po ako babyyyyy :(((("}
