from app.routers.auth import router as auth_router
from app.routers.ingredients import router as ingredients_router
from app.routers.recipes import router as recipes_router
from app.routers.units import router as units_router
from app.routers.upload import router as upload_router
from app.routers.users import router as users_router

__all__ = [
    "auth_router",
    "recipes_router",
    "ingredients_router",
    "units_router",
    "users_router",
    "upload_router",
]
