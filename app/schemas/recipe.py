from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ingredient import IngredientCreate, IngredientPublic
from app.schemas.step import StepCreate, StepPublic


class RecipeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Recipe title")
    description: str = Field(..., description="Detailed description or overview of the recipe")
    category: str = Field(
        ..., min_length=1, max_length=50, description="Main category (e.g. Горячие блюда, Завтраки)"
    )
    subcategory: str | None = Field(
        default=None, max_length=50, description="Subcategory (e.g. супы, напитки, каша)"
    )
    image_path: str | None = Field(
        default=None, max_length=500, description="Image URL or local file path"
    )


class RecipeCreate(RecipeBase):
    ingredients: list[IngredientCreate] = Field(
        default_factory=list, description="List of ingredients with units"
    )
    steps: list[StepCreate] = Field(default_factory=list, description="List of cooking steps")


class RecipeUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = None
    category: str | None = Field(None, min_length=1, max_length=50)
    subcategory: str | None = Field(None, max_length=50)
    image_path: str | None = None
    ingredients: list[IngredientCreate] | None = None
    steps: list[StepCreate] | None = None


class RecipePublic(RecipeBase):
    id: int
    created_at: datetime
    author_id: int | None = None
    author_username: str | None = None
    ingredients: list[IngredientPublic] = Field(default_factory=list)
    steps: list[StepPublic] = Field(default_factory=list)
    rating: float = 0.0
    ratings_count: int = 0
    is_favourite: bool = False

    model_config = ConfigDict(from_attributes=True)


class CategoriesResponse(BaseModel):
    categories: list[str]
    subcategories: list[str]
