from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from app.config import settings
from app.routers import (
    auth_router,
    ingredients_router,
    recipes_router,
    units_router,
    upload_router,
    users_router,
)
from app.seed import seed_demo_data

STATIC_DIR = Path(__file__).parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Recipe Book API",
    description="Recipe management and culinary showcase API with Tortoise-ORM & Pydantic v2",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(recipes_router, prefix="/api")
app.include_router(ingredients_router, prefix="/api")
app.include_router(units_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(upload_router, prefix="/api")

# Static and media files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/", tags=["Web UI"], response_class=FileResponse)
async def root():
    if INDEX_HTML.exists():
        return FileResponse(str(INDEX_HTML))
    return FileResponse(
        {
            "status": "online",
            "message": "Recipe Book API is running!",
            "docs_url": "/docs",
        }
    )


TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "app.models.role",
                "app.models.user",
                "app.models.category",
                "app.models.recipe",
                "app.models.ingredient",
                "app.models.unit",
                "app.models.step",
                "app.models.comment",
            ],
            "default_connection": "default",
        },
    },
}

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.on_event("startup")
async def on_startup():
    await seed_demo_data()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
