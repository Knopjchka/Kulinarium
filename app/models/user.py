from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.role import Role


class User(Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=50, unique=True, db_index=True)
    password_hash = fields.CharField(max_length=255)
    role: fields.ForeignKeyNullableRelation["Role"] = fields.ForeignKeyField(
        "models.Role",
        related_name="users",
        null=True,
        on_delete=fields.SET_NULL,
    )
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    favourite_recipes: fields.ManyToManyRelation["Recipe"] = fields.ManyToManyField(
        "models.Recipe",
        related_name="favourited_by",
        through="user_favourites",
    )

    class Meta:
        table = "users"

    def __str__(self) -> str:
        return f"<User {self.username}>"
