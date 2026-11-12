from pydantic import BaseModel, ConfigDict, Field


class StepBase(BaseModel):
    number: int = Field(..., ge=1, description="Step sequence number")
    text: str = Field(..., min_length=1, description="Step description and instructions")


class StepCreate(StepBase):
    pass


class StepPublic(StepBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
