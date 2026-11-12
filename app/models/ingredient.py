from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from app.models.unit import Unit


class Ingredient(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100, db_index=True)
    unit: fields.ForeignKeyNullableRelation["Unit"] = fields.ForeignKeyField(
        "models.Unit",
        related_name="ingredients",
        null=True,
        on_delete=fields.SET_NULL,
    )

    class Meta:
        table = "ingredients"

    def __str__(self) -> str:
        return f"<Ingredient {self.name}>"
