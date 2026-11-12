from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, require_role
from app.models.user import User
from app.routers.recipes import serialize_recipe
from app.schemas.recipe import RecipePublic
from app.schemas.user import UserPublic

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserPublic], summary="List all users (Admin only)")
async def list_users(_admin: User = Depends(require_role("admin"))) -> list[UserPublic]:
    users = await User.all().prefetch_related("role")
    results = []
    for u in users:
        fav_ids = await u.favourite_recipes.all().values_list("id", flat=True)
        role_name = u.role.name if u.role else "user"
        results.append(
            UserPublic(
                id=u.id,
                username=u.username,
                role=role_name,
                is_active=u.is_active,
                created_at=u.created_at,
                favourite_recipe_ids=list(fav_ids),
            )
        )
    return results


@router.get(
    "/me/favourites",
    response_model=list[RecipePublic],
    summary="Get current user's favourite recipes",
)
async def get_my_favourites(current_user: User = Depends(get_current_user)) -> list[RecipePublic]:
    recipes = await current_user.favourite_recipes.all().prefetch_related(
        "category", "subcategory", "ingredients__unit", "steps", "comments", "author"
    )
    fav_ids = {r.id for r in recipes}
    return [serialize_recipe(r, fav_ids) for r in recipes]
