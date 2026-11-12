from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Comment text")
    rating: float = Field(
        5.0,
        ge=1.0,
        le=5.0,
        description="Rating from 1.0 to 5.0 (supports half stars e.g. 4.5)",
    )


class CommentPublic(BaseModel):
    id: int
    recipe_id: int
    user_id: int
    username: str
    rating: float
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
