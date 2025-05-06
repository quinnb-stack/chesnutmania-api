from bson import ObjectId
from fastapi import Body, Depends, HTTPException, status, APIRouter
from pymongo import ReturnDocument
from app.database import MongoDatabaseSession
from app.users.schemas import User, UserCollection, UpdateUser
from passlib.context import CryptContext

router = APIRouter(tags=["Users Resources"])

get_db = MongoDatabaseSession("sample_users")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/users/{id}", response_model=User)
async def get_user(id: str, db=Depends(get_db)):
    db_user = await db["users"].find_one({"_id": ObjectId(id)})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get(
    "/users/",
    response_description="List all users",
    response_model=UserCollection,
    response_model_by_alias=False,
)
async def list_users(db=Depends(get_db)):
    """
    List all of the user data in the database.

    The response is unpaginated and limited to 1000 results.
    """
    return UserCollection(users=await db["users"].find().to_list(1000))


@router.post(
    "/users/",
    response_description="Add new user",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_user(user: User = Body(...), db=Depends(get_db)):
    """
    Insert a new user record into MongoDB.

    A unique `id` will be created and provided in the response.
    """
    isExist = await db["users"].find_one({"username": user.username})

    if isExist:
        raise HTTPException(status_code=409, detail=f"Username already registered")

    user.password = pwd_context.hash(user.password)

    db_user = await db["users"].insert_one(
        user.model_dump(by_alias=True, exclude=["id"])
    )
    created_user = await db["users"].find_one({"_id": db_user.inserted_id})
    return created_user


@router.put(
    "/users/{id}",
    response_description="Update a user",
    response_model=User,
    response_model_by_alias=False,
)
async def update_user(id: str, user: UpdateUser = Body(...), db=Depends(get_db)):
    """
    Update individual fields of an existing user record.

    Only the provided fields will be updated.
    Any missing or `null` fields will be ignored.
    """
    user = {k: v for k, v in user.model_dump(by_alias=True).items() if v is not None}

    if len(user) >= 1:
        update_result = await db["users"].find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": user},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"User {id} not found")

    # The update is empty, but we should still return the matching document:
    if (existing_user := await db["users"].find_one({"_id": id})) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"User {id} not found")


@router.put(
    "/users/deactivate/{id}",
    response_description="Deactivate a user",
    response_model=User,
    response_model_by_alias=False,
)
async def deactivate_user(id: str, db=Depends(get_db)):
    """
    Deactivate user by setting `isActive` to False.
    """

    db_user = await db["users"].update_one(
        {"_id": ObjectId(id)}, {"$set": {"isActive": False}}
    )

    if db_user.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"User {id} not found")

    # Return the updated user document
    updated_user = await db["users"].find_one({"_id": ObjectId(id)})
    return updated_user


@router.delete("/users/{id}", response_description="Delete a user")
async def delete_user(id: str, db=Depends(get_db)):
    """
    Remove a single user record from the database.
    """
    db_user = await db["users"].delete_one({"_id": ObjectId(id)})

    if db_user.deleted_count == 1:
        return HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"User {id} not found")
