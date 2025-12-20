from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from db.repository import UserRepository
from schemas.entity import UserCreate, UserInDB, UserChangePassword, UserChangeLogin, LoginSchema
from schemas.token import TokenResponse
from services.auth import AuthService

router = APIRouter(prefix="/users")


@router.post('/signup', response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, session: AsyncSession = Depends(get_session)) -> UserInDB:
    """Регистрация пользователя."""
    user_repo = UserRepository(session)

    existing_user = await user_repo.get_user_by_login(user_create.login)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login already registered"
        )

    existing_email = await user_repo.get_user_by_email(user_create.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = await user_repo.create_user(
        login=user_create.login,
        email=user_create.email,
        password=user_create.password,
        first_name=user_create.first_name,
        last_name=user_create.last_name
    )

    return user


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginSchema, request: Request, session: AsyncSession = Depends(get_session), Authorize: AuthJWT = Depends()):
    """Аутентификация."""
    auth_service = AuthService(session, Authorize)
    tokens = await auth_service.login(request, payload.login, payload.password)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
        session: AsyncSession = Depends(get_session),
        Authorize: AuthJWT = Depends()
):
    """Обновление access токена"""
    auth_service = AuthService(session, Authorize)
    return await auth_service.refresh_tokens()


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(session: AsyncSession = Depends(get_session), Authorize: AuthJWT = Depends()):
    """Сброс токенов."""
    auth_service = AuthService(session, Authorize)
    await auth_service.logout()


@router.post("/change-login")
async def change_login(
    payload: UserChangeLogin,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """Смена логина."""
    auth_service = AuthService(session, Authorize)
    await auth_service.change_login(payload.new_login)
    return {"msg": "Login updated"}


@router.post("/change-password")
async def change_password(
    payload: UserChangePassword,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """Смена пароля."""
    auth_service = AuthService(session, Authorize)
    await auth_service.change_password(payload.current_password, payload.new_password)
    return {"msg": "Password updated"}


@router.get("/login-history")
async def login_history(
    limit: int = 50,
    offset: int = 0,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """Получение пользователем своей истории входов в аккаунт."""
    auth_service = AuthService(session, Authorize)
    return await auth_service.login_history(limit, offset)
