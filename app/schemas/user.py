from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="Plain text password")
    role: str | None = Field("user", description="Role: 'user' or 'admin'")


class UserUpdate(BaseModel):
    password: str | None = Field(None, min_length=6, max_length=100)


class UserPublic(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    favourite_recipe_ids: list[int] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
