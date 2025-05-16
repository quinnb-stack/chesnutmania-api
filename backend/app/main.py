from fastapi import FastAPI
from .users import users
from .oauth import oauth

app = FastAPI()

app.mount("/users", users.app)
app.mount("/oauth", oauth.app)


@app.get("/")
def read_root():
    return {"I kiss na gad po ako babyyyyy :(((("}
