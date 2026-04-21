from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ...application.dto import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UserPublic,
)
from ...application.services import AuthService
from ...domain.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidRefreshToken,
    UserInactive,
)
from ..deps import get_auth_service, get_token_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    svc: AuthService = Depends(get_auth_service),
) -> UserPublic:
    try:
        user = await svc.register(payload.email, payload.password)
    except EmailAlreadyRegistered:
        raise HTTPException(status_code=409, detail="email_already_registered") from None
    return UserPublic(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        roles=user.roles,
    )


@router.post("/login", response_model=TokenPair)
async def login(
    payload: LoginRequest,
    svc: AuthService = Depends(get_auth_service),
) -> TokenPair:
    try:
        return await svc.login(payload.email, payload.password)
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="invalid_credentials") from None
    except UserInactive:
        raise HTTPException(status_code=403, detail="user_inactive") from None


@router.post("/token", response_model=TokenPair)
async def token_oauth2(
    form: OAuth2PasswordRequestForm = Depends(),
    svc: AuthService = Depends(get_auth_service),
) -> TokenPair:
    """OAuth2 password grant — compatible con clientes estándar."""
    try:
        return await svc.login(form.username, form.password)
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="invalid_credentials") from None
    except UserInactive:
        raise HTTPException(status_code=403, detail="user_inactive") from None


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: RefreshRequest,
    svc: AuthService = Depends(get_auth_service),
) -> TokenPair:
    try:
        return await svc.refresh(payload.refresh_token)
    except InvalidRefreshToken:
        raise HTTPException(status_code=401, detail="invalid_refresh_token") from None


@router.get("/me")
async def me(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
):
    if not token:
        raise HTTPException(status_code=401, detail="missing_token")
    import jwt as _jwt

    tokens = get_token_service(request)
    try:
        claims = _jwt.decode(
            token,
            tokens._public_key_obj,
            algorithms=[tokens.ALGORITHM],
            audience=tokens._audience,
            issuer=tokens._issuer,
            options={"require": ["exp", "iat", "iss", "sub"]},
        )
    except _jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"invalid_token: {exc}") from exc
    if claims.get("typ") != "access":
        raise HTTPException(status_code=401, detail="not_access_token")
    return {"sub": claims["sub"], "roles": claims.get("roles", [])}
