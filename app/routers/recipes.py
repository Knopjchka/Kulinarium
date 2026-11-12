from fastapi import APIRouter, Depends, HTTPException, Query, status
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from app.dependencies.auth import get_current_user, get_current_user_optional
from app.models.category import Category
from app.models.comment import Comment
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.step import Step
from app.models.unit import Unit
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentPublic
from app.schemas.ingredient import IngredientPublic
from app.schemas.recipe import (
    CategoriesResponse,
    RecipeCreate,
    RecipePublic,
    RecipeUpdate,
)
from app.schemas.step import StepPublic
from app.schemas.unit import UnitPublic

router = APIRouter(prefix="/recipes", tags=["Recipes"])

DEFAULT_CATEGORIES = [
    "Первые блюда",
    "Вторые блюда",
    "Завтраки",
    "Напитки",
    "Выпечка",
    "Салаты",
    "Десерты",
    "Закуски",
]

DEFAULT_SUBCATEGORIES = [
    "супы",
    "напитки",
    "каша",
    "выпечка",
    "салаты",
    "смузи",
    "десерты",
    "гарниры",
]


async def get_or_create_category_hierarchy(
    category_name: str, subcategory_name: str | None = None
) -> tuple[Category | None, Category | None]:
    if not category_name:
        return None, None

    clean_cat = category_name.strip()
    cat_slug = clean_cat.lower().replace(" ", "-")
    cat_obj = await Category.filter(name__iexact=clean_cat, parent_id__isnull=True).first()
    if not cat_obj:
        if await Category.exists(slug=cat_slug):
            cat_slug = f"{cat_slug}-{await Category.all().count() + 1}"
        cat_obj = await Category.create(name=clean_cat, slug=cat_slug)

    subcat_obj = None
    if subcategory_name and subcategory_name.strip():
        clean_sub = subcategory_name.strip()
        subcat_obj = await Category.filter(name__iexact=clean_sub, parent=cat_obj).first()
        if not subcat_obj:
            sub_slug = f"{cat_obj.slug}-{clean_sub.lower().replace(' ', '-')}"
            if await Category.exists(slug=sub_slug):
                sub_slug = f"{sub_slug}-{await Category.all().count() + 1}"
            subcat_obj = await Category.create(name=clean_sub, slug=sub_slug, parent=cat_obj)

    return cat_obj, subcat_obj


def compute_recipe_score(recipe: Recipe, search_term: str) -> float:
    score = 0.0
    term = search_term.strip().lower()
    t_name = recipe.name.lower()
    cat_name = recipe.category.name.lower() if recipe.category else ""
    sub_name = recipe.subcategory.name.lower() if recipe.subcategory else ""
    desc = (recipe.description or "").lower()

    # Exact or prefix match in recipe title
    if t_name == term:
        score += 100.0
    elif t_name.startswith(term):
        score += 70.0
    elif term in t_name:
        score += 50.0

    # Category and subcategory match
    if term == cat_name or term == sub_name:
        score += 45.0
    elif term in cat_name or term in sub_name:
        score += 35.0

    # Ingredients match
    for ing in recipe.ingredients:
        ing_name = ing.name.lower()
        if term == ing_name:
            score += 30.0
        elif term in ing_name:
            score += 20.0

    # Description match
    if term in desc:
        score += 10.0

    return score


def serialize_recipe(recipe: Recipe, fav_ids: set[int]) -> RecipePublic:
    ingredients_list = []
    for ing in recipe.ingredients:
        unit_data = None
        if ing.unit:
            unit_data = UnitPublic(
                id=ing.unit.id,
                name=ing.unit.name,
                quantity=ing.unit.quantity,
            )
        ingredients_list.append(IngredientPublic(id=ing.id, name=ing.name, unit=unit_data))

    steps_list = [
        StepPublic(id=st.id, number=st.number, text=st.text)
        for st in sorted(recipe.steps, key=lambda s: s.number)
    ]

    cat_name = recipe.category.name if recipe.category else ""
    subcat_name = recipe.subcategory.name if recipe.subcategory else None

    # Calculate average rating and count safely
    try:
        ratings = [c.rating for c in recipe.comments if c.rating is not None]
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0.0
        ratings_count = len(ratings)
    except Exception:
        avg_rating = 0.0
        ratings_count = 0

    try:
        author_username = recipe.author.username if recipe.author else None
    except Exception:
        author_username = None

    return RecipePublic(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        category=cat_name,
        subcategory=subcat_name,
        image_path=recipe.image_path,
        created_at=recipe.created_at,
        author_id=recipe.author_id,
        author_username=author_username,
        ingredients=ingredients_list,
        steps=steps_list,
        rating=avg_rating,
        ratings_count=ratings_count,
        is_favourite=recipe.id in fav_ids,
    )


@router.get("", response_model=list[RecipePublic], summary="List recipes with score-ranked search")
async def get_recipes(
    category: str | None = Query(None, description="Filter by category"),
    subcategory: str | None = Query(
        None, description="Filter by subcategory (e.g. супы, напитки, каша)"
    ),
    search: str | None = Query(
        None, description="Unified search term across name, ingredients, category"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User | None = Depends(get_current_user_optional),
) -> list[RecipePublic]:
    query = Recipe.all()

    if category:
        query = query.filter(category__name__iexact=category.strip())

    if subcategory:
        query = query.filter(subcategory__name__iexact=subcategory.strip())

    if search:
        search_term = search.strip()
        variants = list(
            dict.fromkeys(
                [
                    search_term,
                    search_term.lower(),
                    search_term.upper(),
                    search_term.capitalize(),
                    search_term.title(),
                ]
            )
        )
        search_filter = Q()
        for v in variants:
            search_filter |= (
                Q(name__icontains=v)
                | Q(description__icontains=v)
                | Q(ingredients__name__icontains=v)
                | Q(category__name__icontains=v)
                | Q(subcategory__name__icontains=v)
            )
        query = query.filter(search_filter).distinct()

    recipes = await query.prefetch_related(
        "category", "subcategory", "ingredients__unit", "steps", "comments", "author"
    )

    # Rank results by score if search query was provided
    if search and search.strip():
        term = search.strip()
        recipes_scored = [
            (compute_recipe_score(r, term), r)
            for r in recipes
        ]
        # Filter out 0-score and sort by score descending
        recipes_scored = [item for item in recipes_scored if item[0] > 0]
        recipes_scored.sort(key=lambda x: (x[0], x[1].id), reverse=True)
        sorted_recipes = [r for _, r in recipes_scored]
    else:
        sorted_recipes = sorted(recipes, key=lambda r: r.id, reverse=True)

    paginated_recipes = sorted_recipes[skip : skip + limit]

    fav_ids: set[int] = set()
    if current_user:
        fav_ids = set(await current_user.favourite_recipes.all().values_list("id", flat=True))

    return [serialize_recipe(r, fav_ids) for r in paginated_recipes]


@router.get(
    "/categories",
    response_model=CategoriesResponse,
    summary="Get all available categories and subcategories",
)
async def get_categories() -> CategoriesResponse:
    root_cats = await Category.filter(parent_id__isnull=True).values_list("name", flat=True)
    sub_cats = await Category.filter(parent_id__isnull=False).values_list("name", flat=True)

    all_cats = list(dict.fromkeys(DEFAULT_CATEGORIES + [c for c in root_cats if c]))
    all_subcats = list(dict.fromkeys(DEFAULT_SUBCATEGORIES + [s for s in sub_cats if s]))

    return CategoriesResponse(categories=all_cats, subcategories=all_subcats)


@router.get("/{recipe_id}", response_model=RecipePublic, summary="Get recipe details by ID")
async def get_recipe_by_id(
    recipe_id: int,
    current_user: User | None = Depends(get_current_user_optional),
) -> RecipePublic:
    recipe = (
        await Recipe.filter(id=recipe_id)
        .prefetch_related(
            "category", "subcategory", "ingredients__unit", "steps", "comments", "author"
        )
        .first()
    )
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found",
        )

    fav_ids: set[int] = set()
    if current_user:
        fav_ids = set(await current_user.favourite_recipes.all().values_list("id", flat=True))

    return serialize_recipe(recipe, fav_ids)


@router.post(
    "",
    response_model=RecipePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new recipe (All registered users)",
)
async def create_recipe(
    recipe_in: RecipeCreate,
    current_user: User = Depends(get_current_user),
) -> RecipePublic:
    if await Recipe.exists(name=recipe_in.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recipe with name '{recipe_in.name}' already exists",
        )

    async with in_transaction():
        cat_obj, subcat_obj = await get_or_create_category_hierarchy(
            recipe_in.category, recipe_in.subcategory
        )
        recipe = await Recipe.create(
            name=recipe_in.name,
            description=recipe_in.description,
            category=cat_obj,
            subcategory=subcat_obj,
            image_path=recipe_in.image_path or "",
            author=current_user,
        )

        for ing_data in recipe_in.ingredients:
            unit_obj = None
            if ing_data.unit:
                unit_obj = await Unit.create(
                    name=ing_data.unit.name,
                    quantity=ing_data.unit.quantity,
                )
            ing_obj = await Ingredient.create(name=ing_data.name, unit=unit_obj)
            await recipe.ingredients.add(ing_obj)

        for step_data in recipe_in.steps:
            step_obj = await Step.create(
                number=step_data.number,
                text=step_data.text,
            )
            await recipe.steps.add(step_obj)

    full_recipe = (
        await Recipe.filter(id=recipe.id)
        .prefetch_related(
            "category", "subcategory", "ingredients__unit", "steps", "comments", "author"
        )
        .first()
    )
    return serialize_recipe(full_recipe, set())


@router.put("/{recipe_id}", response_model=RecipePublic, summary="Update an existing recipe")
async def update_recipe(
    recipe_id: int,
    recipe_in: RecipeUpdate,
    current_user: User = Depends(get_current_user),
) -> RecipePublic:
    recipe = (
        await Recipe.filter(id=recipe_id)
        .prefetch_related(
            "category", "subcategory", "ingredients__unit", "steps", "comments", "author"
        )
        .first()
    )
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found",
        )

    user_role = current_user.role.name if current_user.role else "user"
    if recipe.author_id != current_user.id and user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this recipe",
        )

    if recipe_in.name is not None and recipe_in.name != recipe.name:
        if await Recipe.exists(name=recipe_in.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Recipe with name '{recipe_in.name}' already exists",
            )
        recipe.name = recipe_in.name

    if recipe_in.description is not None:
        recipe.description = recipe_in.description

    if recipe_in.category is not None or recipe_in.subcategory is not None:
        cur_cat_name = recipe.category.name if recipe.category else ""
        cur_sub_name = recipe.subcategory.name if recipe.subcategory else None
        target_cat = recipe_in.category if recipe_in.category is not None else cur_cat_name
        target_sub = recipe_in.subcategory if recipe_in.subcategory is not None else cur_sub_name
        cat_obj, subcat_obj = await get_or_create_category_hierarchy(target_cat, target_sub)
        recipe.category = cat_obj
        recipe.subcategory = subcat_obj

    if recipe_in.image_path is not None:
        recipe.image_path = recipe_in.image_path

    async with in_transaction():
        await recipe.save()

        if recipe_in.ingredients is not None:
            await recipe.ingredients.clear()
            for ing_data in recipe_in.ingredients:
                unit_obj = None
                if ing_data.unit:
                    unit_obj = await Unit.create(
                        name=ing_data.unit.name,
                        quantity=ing_data.unit.quantity,
                    )
                ing_obj = await Ingredient.create(name=ing_data.name, unit=unit_obj)
                await recipe.ingredients.add(ing_obj)

        if recipe_in.steps is not None:
            await recipe.steps.clear()
            for step_data in recipe_in.steps:
                step_obj = await Step.create(
                    number=step_data.number,
                    text=step_data.text,
                )
                await recipe.steps.add(step_obj)

    full_recipe = (
        await Recipe.filter(id=recipe.id)
        .prefetch_related(
            "category", "subcategory", "ingredients__unit", "steps", "comments", "author"
        )
        .first()
    )
    fav_ids: set[int] = set()
    if current_user:
        fav_ids = set(await current_user.favourite_recipes.all().values_list("id", flat=True))
    return serialize_recipe(full_recipe, fav_ids)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a recipe")
async def delete_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
) -> None:
    recipe = await Recipe.get_or_none(id=recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found",
        )

    user_role = current_user.role.name if current_user.role else "user"
    if recipe.author_id != current_user.id and user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this recipe",
        )

    await recipe.delete()
    return None


@router.post(
    "/{recipe_id}/favourite",
    summary="Toggle recipe favourite status for the authenticated user",
)
async def toggle_favourite(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
):
    recipe = await Recipe.get_or_none(id=recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found",
        )

    is_fav = await current_user.favourite_recipes.filter(id=recipe_id).exists()
    if is_fav:
        await current_user.favourite_recipes.remove(recipe)
        return {"favourite": False, "recipe_id": recipe_id}
    else:
        await current_user.favourite_recipes.add(recipe)
        return {"favourite": True, "recipe_id": recipe_id}


# --- Comments & Rating Endpoints ---


@router.get(
    "/{recipe_id}/comments",
    response_model=list[CommentPublic],
    summary="Get comments and ratings for a recipe",
)
async def get_recipe_comments(recipe_id: int) -> list[CommentPublic]:
    recipe = await Recipe.get_or_none(id=recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found",
        )

    comments = (
        await Comment.filter(recipe_id=recipe_id)
        .prefetch_related("user")
        .order_by("-created_at")
    )

    return [
        CommentPublic(
            id=c.id,
            recipe_id=c.recipe_id,
            user_id=c.user_id,
            username=c.user.username if c.user else "Пользователь",
            rating=c.rating,
            text=c.text,
            created_at=c.created_at,
        )
        for c in comments
    ]


@router.post(
    "/{recipe_id}/comments",
    response_model=CommentPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment with star rating (All registered users)",
)
async def create_recipe_comment(
    recipe_id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
) -> CommentPublic:
    recipe = await Recipe.get_or_none(id=recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found",
        )

    # Round rating to nearest 0.5
    rating_val = round(comment_in.rating * 2) / 2
    rating_val = max(1.0, min(5.0, rating_val))

    comment = await Comment.create(
        recipe=recipe,
        user=current_user,
        rating=rating_val,
        text=comment_in.text.strip(),
    )

    return CommentPublic(
        id=comment.id,
        recipe_id=comment.recipe_id,
        user_id=comment.user_id,
        username=current_user.username,
        rating=comment.rating,
        text=comment.text,
        created_at=comment.created_at,
    )


@router.delete(
    "/{recipe_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment (Comment author or Admin only)",
)
async def delete_recipe_comment(
    recipe_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
) -> None:
    comment = await Comment.filter(id=comment_id, recipe_id=recipe_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found",
        )

    user_role = current_user.role.name if current_user.role else "user"
    if comment.user_id != current_user.id and user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment",
        )

    await comment.delete()
    return None
