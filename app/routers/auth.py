from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserPublic
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(user_in: UserCreate) -> UserPublic:
    if await User.exists(username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken",
        )

    role_name = user_in.role if user_in.role in ["user", "admin"] else "user"
    role_obj, _ = await Role.get_or_create(
        name=role_name, defaults={"description": f"Role {role_name}"}
    )

    user = await User.create(
        username=user_in.username,
        password_hash=hash_password(user_in.password),
        role=role_obj,
    )

    return UserPublic(
        id=user.id,
        username=user.username,
        role=role_name,
        is_active=user.is_active,
        created_at=user.created_at,
        favourite_recipe_ids=[],
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT access token",
)
async def login(credentials: LoginRequest) -> TokenResponse:
    user = await User.filter(username=credentials.username).prefetch_related("role").first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    role_name = user.role.name if user.role else "user"
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": role_name}
    )
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get current authenticated user profile",
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserPublic:
    fav_ids = await current_user.favourite_recipes.all().values_list("id", flat=True)
    role_name = current_user.role.name if current_user.role else "user"
    return UserPublic(
        id=current_user.id,
        username=current_user.username,
        role=role_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        favourite_recipe_ids=list(fav_ids),
    )
