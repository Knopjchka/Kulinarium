from tortoise import fields
from tortoise.models import Model


class Unit(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=50)
    quantity = fields.FloatField(default=1.0)

    class Meta:
        table = "units"

    def __str__(self) -> str:
        return f"<Unit {self.name} ({self.quantity})>"
