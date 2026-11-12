from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    pass


class Category(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100, db_index=True)
    slug = fields.CharField(max_length=100, unique=True, db_index=True)
    description = fields.TextField(null=True)

    # Hierarchical link: a subcategory has parent pointing to main Category
    parent: fields.ForeignKeyNullableRelation["Category"] = fields.ForeignKeyField(
        "models.Category",
        related_name="children",
        null=True,
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "categories"

    def __str__(self) -> str:
        return f"<Category {self.name}>"
