from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.user import User


class Comment(Model):
    id = fields.IntField(primary_key=True)
    recipe: fields.ForeignKeyRelation["Recipe"] = fields.ForeignKeyField(
        "models.Recipe",
        related_name="comments",
        on_delete=fields.CASCADE,
    )
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User",
        related_name="comments",
        on_delete=fields.CASCADE,
    )
    rating = fields.FloatField(default=5.0)
    text = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "comments"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"<Comment {self.id} on Recipe {self.recipe_id}>"
