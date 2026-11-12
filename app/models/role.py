from tortoise import fields
from tortoise.models import Model


class Role(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=20, unique=True, db_index=True)
    description = fields.CharField(max_length=150, null=True)

    class Meta:
        table = "roles"

    def __str__(self) -> str:
        return f"<Role {self.name}>"
