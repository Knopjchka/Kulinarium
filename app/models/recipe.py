from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.comment import Comment
    from app.models.ingredient import Ingredient
    from app.models.step import Step
    from app.models.user import User


class Recipe(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100, unique=True, db_index=True)
    description = fields.TextField()
    category: fields.ForeignKeyNullableRelation["Category"] = fields.ForeignKeyField(
        "models.Category",
        related_name="recipes",
        null=True,
        on_delete=fields.SET_NULL,
    )
    subcategory: fields.ForeignKeyNullableRelation["Category"] = fields.ForeignKeyField(
        "models.Category",
        related_name="subcategory_recipes",
        null=True,
        on_delete=fields.SET_NULL,
    )
    image_path = fields.CharField(max_length=500, null=True, default="")
    created_at = fields.DatetimeField(auto_now_add=True)

    author: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        "models.User",
        related_name="recipes",
        null=True,
        on_delete=fields.SET_NULL,
    )
    ingredients: fields.ManyToManyRelation["Ingredient"] = fields.ManyToManyField(
        "models.Ingredient",
        related_name="recipes",
        through="recipe_ingredients",
    )
    steps: fields.ManyToManyRelation["Step"] = fields.ManyToManyField(
        "models.Step",
        related_name="recipes",
        through="recipe_steps",
    )
    comments: fields.ReverseRelation["Comment"]

    class Meta:
        table = "recipes"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"<Recipe {self.name}>"
