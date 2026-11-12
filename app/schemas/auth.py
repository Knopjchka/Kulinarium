from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Schema for authenticating a user with username and password."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for returning a JWT access token to the client."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema representing the decoded JWT payload."""

    sub: str | None = None
    role: str | None = None
    exp: int | None = None
