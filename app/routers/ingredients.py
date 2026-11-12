from fastapi import APIRouter, Query, status

from app.models.ingredient import Ingredient
from app.models.unit import Unit
from app.schemas.ingredient import IngredientCreate, IngredientPublic
from app.schemas.unit import UnitPublic

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


@router.get("", response_model=list[IngredientPublic], summary="List all ingredients")
async def list_ingredients(
    search: str | None = Query(None, description="Search ingredients by name"),
) -> list[IngredientPublic]:
    query = Ingredient.all()
    if search:
        query = query.filter(name__icontains=search.strip())

    items = await query.prefetch_related("unit").limit(100)
    result = []
    for item in items:
        unit_data = None
        if item.unit:
            unit_data = UnitPublic(
                id=item.unit.id,
                name=item.unit.name,
                quantity=item.unit.quantity,
            )
        result.append(IngredientPublic(id=item.id, name=item.name, unit=unit_data))
    return result


@router.post(
    "",
    response_model=IngredientPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create an ingredient",
)
async def create_ingredient(ing_in: IngredientCreate) -> IngredientPublic:
    unit_obj = None
    if ing_in.unit:
        unit_obj = await Unit.create(
            name=ing_in.unit.name,
            quantity=ing_in.unit.quantity,
        )
    item = await Ingredient.create(name=ing_in.name, unit=unit_obj)
    unit_data = (
        UnitPublic(id=unit_obj.id, name=unit_obj.name, quantity=unit_obj.quantity)
        if unit_obj
        else None
    )
    return IngredientPublic(id=item.id, name=item.name, unit=unit_data)
