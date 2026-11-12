from tortoise import fields
from tortoise.models import Model


class Step(Model):
    id = fields.IntField(primary_key=True)
    number = fields.IntegerField()
    text = fields.TextField()

    class Meta:
        table = "steps"
        ordering = ["number"]

    def __str__(self) -> str:
        return f"<Step {self.number}>"
