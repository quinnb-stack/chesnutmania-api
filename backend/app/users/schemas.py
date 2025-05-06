from pydantic import BaseModel, Field
from typing import List, Optional, Any
from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any, _info: Any) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: Any, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string", "example": "60dbf9f531d5b12a1c8b4567"}


class User(BaseModel):
    """
    Container for a user record.
    """

    # The primary key for the UserModel, stored as a `str` on the instance.
    # This will be aliased to `_id` when sent to MongoDB,
    # but provided as `id` in the API requests and responses.
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(...)
    name: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)
    isActive: bool = Field(...)

    class Config:
        # Used for JSON encoding/decoding
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}  # Fix for serialization
        json_schema_extra = {
            "example": {
                "username": "janedoe",
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "password": "asasada1232",
                "isActive": True,
            }
        }


class UpdateUser(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    isActive: bool = None

    class Config:
        # Used for JSON encoding/decoding
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}  # Fix for serialization
        json_schema_extra = {
            "example": {
                "username": "janedoe",
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "password": "asasada1232",
                "isActive": True,
            }
        }


class UserCollection(BaseModel):
    """
    A container holding a list of `UserModel` instances.
    """

    users: List[User]
