from tortoise.transactions import in_transaction

from app.models.category import Category
from app.models.comment import Comment
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.role import Role
from app.models.step import Step
from app.models.unit import Unit
from app.models.user import User
from app.utils.security import hash_password

DEMO_RECIPES = [
    {
        "name": "Борщ классический с говядиной",
        "description": (
            "Наваристый традиционный борщ с насыщенным свекольным цветом, нежным мясом "
            "и ароматом чеснока. Идеально подавать со сметаной и ржаным хлебом."
        ),
        "category": "Первые блюда",
        "subcategory": "супы",
        "image_path": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",
        "ingredients": [
            {"name": "Говядина на кости", "unit": {"name": "г", "quantity": 500}},
            {"name": "Свекла", "unit": {"name": "шт", "quantity": 2}},
            {"name": "Капуста белокочанная", "unit": {"name": "г", "quantity": 300}},
            {"name": "Картофель", "unit": {"name": "шт", "quantity": 3}},
            {"name": "Морковь", "unit": {"name": "шт", "quantity": 1}},
            {"name": "Томатная паста", "unit": {"name": "ст. л.", "quantity": 2}},
            {"name": "Чеснок", "unit": {"name": "зубчик", "quantity": 3}},
        ],
        "steps": [
            {
                "number": 1,
                "text": "Сварить крепкий бульон из говядины (варить 1.5 часа, снимая пену).",
            },
            {
                "number": 2,
                "text": (
                    "Очистить картофель кубиками, капусту нашинковать и добавить в бульон."
                ),
            },
            {
                "number": 3,
                "text": (
                    "Свеклу и морковь натереть соломкой, обжарить с томатной пастой и соком лимона."
                ),
            },
            {
                "number": 4,
                "text": "Переложить зажарку в кастрюлю, посолить, поперчить и варить 10 минут.",
            },
            {
                "number": 5,
                "text": "Добавить измельченный чеснок, выключить огонь и дать настояться 20 минут.",
            },
        ],
    },
    {
        "name": "Овсяная каша с лесными ягодами",
        "description": (
            "Полезный завтрак на молоке с добавлением натурального меда, "
            "сливочного масла и свежих ягод."
        ),
        "category": "Завтраки",
        "subcategory": "каша",
        "image_path": "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?auto=format&fit=crop&w=800&q=80",
        "ingredients": [
            {"name": "Овсяные хлопья", "unit": {"name": "г", "quantity": 100}},
            {"name": "Молоко 3.2%", "unit": {"name": "мл", "quantity": 250}},
            {"name": "Вода", "unit": {"name": "мл", "quantity": 100}},
            {"name": "Мед цветочный", "unit": {"name": "ст. л.", "quantity": 1}},
            {"name": "Масло сливочное", "unit": {"name": "г", "quantity": 20}},
            {"name": "Свежие ягоды", "unit": {"name": "г", "quantity": 60}},
        ],
        "steps": [
            {
                "number": 1,
                "text": "Смешать молоко и воду в сотейнике, довести до закипания на среднем огне.",
            },
            {
                "number": 2,
                "text": (
                    "Всыпать хлопья, варить 7-10 минут на минимальном огне, непрерывно помешивая."
                ),
            },
            {
                "number": 3,
                "text": "Добавить щепотку соли и сливочное масло, закрыть крышкой на 3 минуты.",
            },
            {
                "number": 4,
                "text": "Выложить в тарелку, полить ложкой меда и украсить свежими ягодами.",
            },
        ],
    },
    {
        "name": "Домашний лимонад с мятой и имбирем",
        "description": (
            "Бодрящий напиток из свежего цитрусового сока с пряными нотками имбиря "
            "и ароматной мяты."
        ),
        "category": "Напитки",
        "subcategory": "напитки",
        "image_path": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80",
        "ingredients": [
            {"name": "Лимоны", "unit": {"name": "шт", "quantity": 3}},
            {"name": "Свежая мята", "unit": {"name": "пучок", "quantity": 1}},
            {"name": "Корень имбиря", "unit": {"name": "г", "quantity": 20}},
            {"name": "Сахар тростниковый", "unit": {"name": "г", "quantity": 80}},
            {"name": "Минеральная вода газированная", "unit": {"name": "мл", "quantity": 1000}},
            {"name": "Лед", "unit": {"name": "г", "quantity": 200}},
        ],
        "steps": [
            {
                "number": 1,
                "text": "Выжать сок из лимонов. Корень имбиря очистить и натереть на мелкой терке.",
            },
            {
                "number": 2,
                "text": (
                    "В кувшине размять листики мяты с сахаром и тертым имбирем до появления сока."
                ),
            },
            {
                "number": 3,
                "text": "Влить сок лимона, перемешать до растворения сахара.",
            },
            {
                "number": 4,
                "text": "Залить холодной газированной водой, добавить кубики льда и дольки лимона.",
            },
        ],
    },
    {
        "name": "Нежный тыквенный крем-суп",
        "description": (
            "Бархатистый суп-пюре с легкой сладостью тыквы, сливками и тыквенными семечками."
        ),
        "category": "Первые блюда",
        "subcategory": "супы",
        "image_path": "https://images.unsplash.com/photo-1476718406336-bb5a9690ee2a?auto=format&fit=crop&w=800&q=80",
        "ingredients": [
            {"name": "Мякоть тыквы", "unit": {"name": "г", "quantity": 600}},
            {"name": "Сливки 20%", "unit": {"name": "мл", "quantity": 150}},
            {"name": "Лук репчатый", "unit": {"name": "шт", "quantity": 1}},
            {"name": "Овощной бульон", "unit": {"name": "мл", "quantity": 400}},
            {"name": "Мускатный орех", "unit": {"name": "щепотка", "quantity": 1}},
            {"name": "Тыквенные семечки", "unit": {"name": "г", "quantity": 30}},
        ],
        "steps": [
            {
                "number": 1,
                "text": "Нарезать тыкву и лук, обжарить в сотейнике на оливковом масле.",
            },
            {
                "number": 2,
                "text": "Влить горячий бульон и варить около 20 минут до мягкости тыквы.",
            },
            {
                "number": 3,
                "text": (
                    "Снять с огня, пробить блендером до гладкой шелковистой консистенции."
                ),
            },
            {
                "number": 4,
                "text": "Влить теплые сливки, мускатный орех, соль, прогреть 2 минуты.",
            },
            {
                "number": 5,
                "text": "Разлить по тарелкам, украсить каплями сливок и обжаренными семечками.",
            },
        ],
    },
]


async def seed_demo_data() -> None:
    # Always ensure roles exist
    admin_role, _ = await Role.get_or_create(
        name="admin",
        defaults={"description": "System Administrator"},
    )
    user_role, _ = await Role.get_or_create(
        name="user",
        defaults={"description": "Standard Registered User"},
    )

    # Always ensure admin and demo users exist with linked Role
    admin_user, _ = await User.get_or_create(
        username="admin",
        defaults={
            "password_hash": hash_password("admin123"),
            "role": admin_role,
            "is_active": True,
        },
    )

    await User.get_or_create(
        username="user",
        defaults={
            "password_hash": hash_password("user123"),
            "role": user_role,
            "is_active": True,
        },
    )

    if await Recipe.all().count() > 0:
        return

    async with in_transaction():
        for recipe_dict in DEMO_RECIPES:
            cat_name = recipe_dict["category"]
            subcat_name = recipe_dict["subcategory"]

            cat_slug = cat_name.lower().replace(" ", "-")
            cat_obj, _ = await Category.get_or_create(
                name=cat_name,
                defaults={"slug": cat_slug},
            )

            subcat_obj = None
            if subcat_name:
                subcat_slug = f"{cat_slug}-{subcat_name.lower().replace(' ', '-')}"
                subcat_obj, _ = await Category.get_or_create(
                    name=subcat_name,
                    defaults={"slug": subcat_slug, "parent": cat_obj},
                )

            recipe = await Recipe.create(
                name=recipe_dict["name"],
                description=recipe_dict["description"],
                category=cat_obj,
                subcategory=subcat_obj,
                image_path=recipe_dict["image_path"],
                author=admin_user,
            )

            for ing_data in recipe_dict["ingredients"]:
                unit_dict = ing_data["unit"]
                unit_obj = await Unit.create(
                    name=unit_dict["name"],
                    quantity=unit_dict["quantity"],
                )
                ing_obj = await Ingredient.create(
                    name=ing_data["name"],
                    unit=unit_obj,
                )
                await recipe.ingredients.add(ing_obj)

            for step_data in recipe_dict["steps"]:
                step_obj = await Step.create(
                    number=step_data["number"],
                    text=step_data["text"],
                )
                await recipe.steps.add(step_obj)

            # Seed sample review with rating
            await Comment.create(
                recipe=recipe,
                user=admin_user,
                rating=4.5 if "Борщ" in recipe.name else 5.0,
                text="Превосходный сбалансированный рецепт! Получилось вкусно с первого раза.",
            )
