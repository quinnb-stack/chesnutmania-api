from fastapi import Depends, HTTPException, FastAPI
from requests import Session
from app.database import MongoDatabaseSession
from app.oauth.schemas import Token, TokenData
from app.users.schemas import User
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Annotated, Optional
from passlib.context import CryptContext

app = FastAPI(title="Oauth2")

get_db = MongoDatabaseSession("sample_users")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_HOURS = 720

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=2)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_user(username: str, password: Optional[str] = None, db=Depends(get_db)):
    user = await db["users"].find_one({"username": username})
    if not user or "password" not in user or not user["password"]:
        return None

    # Ensure both inputs are strings
    if not password or not isinstance(password, str):
        return None

    if not verify_password(password, user["password"]):
        return None

    return User(**user)  # Parse into a Pydantic model


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:
        return None
    user = await get_user(username=token_data.username, db=db)
    if user is None:
        return None
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/token/", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db=Depends(get_db),
):
    # Call your async MongoDB-based get_user function
    user = await get_user(form_data.username, form_data.password, db=db)

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(hours=ACCESS_TOKEN_HOURS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/verify/")
async def validate_jwt(current_user: User = Depends(get_current_active_user)):
    if current_user is None:
        # Better to raise HTTPException (lets FastAPI handle headers properly)
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"active": True}
