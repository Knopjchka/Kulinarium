from fastapi import APIRouter, status

from app.models.unit import Unit
from app.schemas.unit import UnitCreate, UnitPublic

router = APIRouter(prefix="/units", tags=["Units"])


@router.get("", response_model=list[UnitPublic], summary="List all units")
async def list_units() -> list[UnitPublic]:
    units = await Unit.all().limit(100)
    return [UnitPublic.model_validate(u) for u in units]


@router.post(
    "", response_model=UnitPublic, status_code=status.HTTP_201_CREATED, summary="Create a unit"
)
async def create_unit(unit_in: UnitCreate) -> UnitPublic:
    unit = await Unit.create(name=unit_in.name, quantity=unit_in.quantity)
    return UnitPublic.model_validate(unit)
