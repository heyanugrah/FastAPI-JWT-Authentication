
#This takes over the job of validating the JSON payloads coming into and going out of your API.
from typing import Optional
from pydantic import BaseModel


# Base properties shared across multiple schemas
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    role: str
    disabled: Optional[bool] = False


# Used when a user registers (requires plain password)
class UserCreate(UserBase):
    password: str


# Used when returning user data to the client (includes DB ID, excludes password)
class User(UserBase):
    id: int

    # Tells Pydantic to read data from SQLAlchemy objects
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
