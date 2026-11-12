from pydantic import BaseModel, ConfigDict, Field


class UnitBase(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=50, description="Unit name, e.g. g, ml, pcs, tbsp"
    )
    quantity: float = Field(..., gt=0, description="Amount/quantity, e.g. 200, 1.5")


class UnitCreate(UnitBase):
    pass


class UnitPublic(UnitBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
