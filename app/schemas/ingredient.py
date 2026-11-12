from pydantic import BaseModel, ConfigDict, Field

from app.schemas.unit import UnitCreate, UnitPublic


class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Ingredient name")


class IngredientCreate(IngredientBase):
    unit: UnitCreate | None = Field(
        default=None, description="Optional unit measurement and quantity"
    )


class IngredientPublic(IngredientBase):
    id: int
    unit: UnitPublic | None = None

    model_config = ConfigDict(from_attributes=True)
