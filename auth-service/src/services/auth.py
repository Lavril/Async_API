import uuid
from async_fastapi_jwt_auth.exceptions import MissingTokenError, JWTDecodeError, AccessTokenRequired
from fastapi import Request, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.redis_db import store_refresh_token, revoke_refresh_token, revoke_access_token
from db.repository import UserRepository, LoginHistoryRepository
from core.security import verify_password
from models.entity import User
from schemas.token import TokenResponse
from async_fastapi_jwt_auth import AuthJWT
from services.permission_service import PermissionService


class AuthService:
    def __init__(self, db: AsyncSession, auth: AuthJWT):
        self.db = db
        self.user_repo = UserRepository(db)
        self.history_repo = LoginHistoryRepository(db)
        self.auth = auth

    async def authenticate_user(
            self,
            login: str,
            password: str
    ) -> dict | None:
        """Сервис для аутентификации пользователя."""
        user = await self.user_repo.get_user_by_login(login)
        if not user or not verify_password(password, user.password):
            return None

        # Get user roles and permissions
        user_roles = await self.user_repo.get_user_role_names(user.id)
        user_permissions = await self.user_repo.get_user_permissions(user.id)
        user_priority = await self.user_repo.get_highest_role_priority(user.id)
        
        return {
            "id": str(user.id),
            "login": user.login,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": user_roles,
            "permissions": user_permissions,
            "highest_role_priority": user_priority,
            "primary_role": user_roles[0] if user_roles else "user"
        }

    async def login(
            self,
            request: Request,
            login: str,
            password: str
    ) -> TokenResponse | None:
        """Login user and return tokens"""
        user = await self.authenticate_user(login, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password"
            )

        # Create access and refresh tokens with new user data
        token_claims = {
            "user_id": user["id"], 
            "roles": user["roles"],
            "permissions": user["permissions"],
            "highest_role_priority": user["highest_role_priority"],
            "primary_role": user["primary_role"],
            "email": user.get("email")
        }
        
        access_token = await self.auth.create_access_token(
            subject=user["login"],
            user_claims=token_claims
        )

        refresh_token = await self.auth.create_refresh_token(
            subject=user["login"],
            user_claims=token_claims
        )

        # Store refresh token in Redis
        new_raw = await self.auth.get_raw_jwt(refresh_token)
        await store_refresh_token(new_raw["jti"], str(user.get("id")), new_raw["exp"])

        # Create login history record
        user_agent = request.headers.get("user-agent")
        login_info = ""
        await self.history_repo.create_login_record(
            user_id=user["id"],
            user_agent=user_agent,
            login_info=login_info
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_tokens(
            self,
    ):
        await self.auth.jwt_refresh_token_required()

        user_claims = await self.auth.get_raw_jwt()

        # Проверка наличия refresh token
        jti = user_claims.get("jti")

        # Удаление старого refresh token
        await revoke_refresh_token(jti)

        # Удаление старого access token
        try:
            access_jti = user_claims.get("access_jti")
            access_exp = user_claims.get("access_exp")
            if access_jti and access_exp:
                await revoke_access_token(access_jti, access_exp)
        except Exception:
            pass

        # Получаем данные из текущего токена
        current_user = await self.auth.get_jwt_subject()

        # Создаем новый access токен с обновленными claims
        token_claims = {
            "user_id": user_claims.get("user_id"),
            "roles": user_claims.get("roles", []),
            "permissions": user_claims.get("permissions", 0),
            "highest_role_priority": user_claims.get("highest_role_priority", 0),
            "primary_role": user_claims.get("primary_role", "user"),
            "email": user_claims.get("email")
        }
        
        new_access_token = await self.auth.create_access_token(
            subject=current_user,
            user_claims=token_claims
        )

        refresh_token = await self.auth.create_refresh_token(
            subject=current_user,
            user_claims=token_claims
        )
        new_raw = await self.auth.get_raw_jwt(refresh_token)
        await store_refresh_token(new_raw["jti"], user_claims.get("user_id"), new_raw["exp"])

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def logout(
            self,
    ) -> None:
        """Logout user."""
        try:
            await self.auth.jwt_required()
        except AccessTokenRequired:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token required."
            )
        except MissingTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Требуется авторизация. Отсутствует токен."
            )
        except JWTDecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный или просроченный токен."
            )

        access_raw = await self.auth.get_raw_jwt()
        await revoke_access_token(access_raw["jti"], access_raw["exp"])

        try:
            await self.auth.jwt_refresh_token_required()
            refresh_raw = await self.auth.get_raw_jwt()
            await revoke_refresh_token(refresh_raw["jti"])
        except Exception:
            pass

    async def login_history(
        self,
        limit: int,
        offset: int
    ):
        """Сервис для получения пользователем своей истории входов в аккаунт """
        await self.auth.jwt_required()

        claims = await self.auth.get_raw_jwt()
        user_id = uuid.UUID(claims["user_id"])  # Convert string back to UUID

        history = await self.history_repo.get_user_login_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        return history

    async def change_login(self, new_login: str):
        """Сервис для смены логина."""

        await self.auth.jwt_required()

        claims = await self.auth.get_raw_jwt()
        user_id = uuid.UUID(claims["user_id"])  # Convert string back to UUID

        try:
            await self.user_repo.update_user_login(user_id, new_login)
        except IntegrityError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Login already in use")

    async def change_password(self, current_password: str, new_password: str):
        """Сервис для смены пароля."""
        await self.auth.jwt_required()

        claims = await self.auth.get_raw_jwt()
        user_id = uuid.UUID(claims["user_id"])  # Convert string back to UUID

        if not await self.user_repo.verify_user_password(user_id, current_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Current password incorrect")

        await self.user_repo.update_user_password(user_id, new_password)
