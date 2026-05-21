"""Routes de autenticación."""

import logging

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.application.services.telegram_auth_code_service import (
    get_telegram_auth_code_service,
)
from src.core.application.services.user_service import UserService
from src.infrastructure.api.v1.deps import get_user_service
from src.shared.config import settings
from src.shared.schemas.auth import (
    AuthResponse,
    CodeSentResponse,
    EmailLoginRequest,
    EmailRegisterRequest,
    RefreshTokenRequest,
    TelegramAutoRegisterRequest,
    TelegramCodeRequest,
    TelegramVerifyRequest,
)
from src.shared.security.jwt import create_token_pair, revoke_token
from src.shared.security.telegram_auth import (
    extract_user_from_telegram_data,
    validate_telegram_init_data,
)

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/telegram",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def authenticate_telegram(
    request: Request,
    init_data: str = Form(..., description="Telegram WebApp initData"),
    user_service: UserService = Depends(get_user_service),
):
    """
    Autentica usuario con Telegram WebApp initData.

    Valida el initData de Telegram y retorna JWT token.

    Args:
        request: Request object
        init_data: Telegram WebApp initData (form field)
        user_service: Servicio de usuarios

    Returns:
        AuthResponse: Token JWT y datos de autenticación

    Raises:
        HTTPException: 401 si el initData es inválido
    """
    # Validar initData
    telegram_data = validate_telegram_init_data(init_data)
    if not telegram_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData",
        )

    # Extraer datos del usuario
    user_info = extract_user_from_telegram_data(telegram_data)

    # Buscar o crear usuario
    user = user_service.get_or_create_by_telegram(
        telegram_id=user_info["telegram_id"],
        username=user_info.get("username"),
        first_name=user_info.get("first_name"),
        last_name=user_info.get("last_name"),
    )

    # Generar JWT
    access_token, refresh_token = create_token_pair(user.id, user.telegram_id)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Revoca el token JWT actual (logout).

    Args:
        request: Request object
        credentials: JWT token credentials

    Returns:
        dict: Mensaje de confirmación
    """
    token = credentials.credentials
    revoke_token(token, settings.JWT_EXPIRATION_HOURS * 3600)
    return {"message": "Logged out successfully"}


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def register_email(
    request: Request,
    register_data: EmailRegisterRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Registra nuevo usuario con email/password.

    Args:
        request: Request object
        register_data: Datos de registro (email, password, display_name)
        user_service: Servicio de usuarios

    Returns:
        AuthResponse: Tokens de acceso

    Raises:
        HTTPException: 400 si el email ya existe
    """
    # Check if email already exists
    existing = user_service.get_by_email(register_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user with email/password
    user = user_service.create_with_email(
        email=register_data.email,
        password=register_data.password,
        display_name=register_data.display_name,
    )

    # Generate token pair
    access_token, refresh_token = create_token_pair(user.id)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def login_email(
    request: Request,
    login_data: EmailLoginRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Autentica usuario con email/password.

    Args:
        request: Request object
        login_data: Credenciales (email, password)
        user_service: Servicio de usuarios

    Returns:
        AuthResponse: Tokens de acceso

    Raises:
        HTTPException: 401 si las credenciales son inválidas
    """
    # Authenticate user
    user = user_service.authenticate_email(
        email=login_data.email,
        password=login_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate token pair
    access_token, refresh_token = create_token_pair(user.id)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
    )


@router.post(
    "/telegram/auto-register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def auto_register_telegram(
    request: Request,
    auto_register: TelegramAutoRegisterRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Registro automático de usuario desde Telegram Bot.

    Crea o busca usuario por telegram_id y retorna tokens JWT.
    Usado para autenticación invisible en el bot.

    Si se proporcionan datos de perfil de Telegram (username, first_name, last_name),
    se actualiza la información del usuario existente o se usa para crear el nuevo usuario.

    Args:
        request: Request object
        auto_register: telegram_id y datos de perfil opcionales
        user_service: Servicio de usuarios

    Returns:
        AuthResponse: Tokens de acceso

    Note:
        Este endpoint es usado exclusivamente por el Telegram Bot
        para autenticación invisible (sin intervención del usuario).
    """
    # Get or create user by telegram_id with profile data
    user = user_service.get_or_create_by_telegram(
        telegram_id=auto_register.telegram_id,
        username=auto_register.username,
        first_name=auto_register.first_name,
        last_name=auto_register.last_name,
    )

    # Generate token pair
    access_token, refresh_token = create_token_pair(user.id, user.telegram_id)

    logger.info(
        f"Auto-registered telegram user: {user.id} (telegram_id={auto_register.telegram_id}, username={auto_register.username})"
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
    )


@router.post(
    "/refresh",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def refresh_access_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Renueva access token usando refresh token.

    Args:
        request: Request object
        refresh_data: {"refresh_token": str}
        user_service: Servicio de usuarios

    Returns:
        AuthResponse: Nuevos tokens

    Raises:
        HTTPException: 401 si el refresh token es inválido
    """
    from src.shared.security.jwt import decode_jwt_token

    refresh_token_str = refresh_data.refresh_token
    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    # Decode and validate refresh token
    try:
        payload = decode_jwt_token(refresh_token_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from None

    # Check token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # Get user
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Generate new token pair
    access_token, new_refresh_token = create_token_pair(user.id)

    return AuthResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
    )


@router.post(
    "/telegram/request-code",
    response_model=CodeSentResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def request_telegram_code(
    request: Request,
    code_request: TelegramCodeRequest,
    user_service: UserService = Depends(get_user_service),
    auth_code_service=Depends(get_telegram_auth_code_service),
):
    """
    Solicita código de autenticación vía Telegram.

    Envía un código de 6 dígitos al usuario vía Telegram.
    El código expira en 5 minutos y es de un solo uso.

    Args:
        request: Request object
        code_request: telegram_id del usuario
        user_service: Servicio de usuarios
        auth_code_service: Servicio de códigos de auth

    Returns:
        CodeSentResponse: Confirmación de envío

    Raises:
        HTTPException: 404 si el usuario no existe
    """
    # Verify user exists
    user = user_service.get_by_telegram_id(code_request.telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Create and send auth code
    auth_code_service.create_code(code_request.telegram_id)

    return CodeSentResponse(
        success=True,
        message=f"Code sent to Telegram user {code_request.telegram_id}",
        expires_in=300,  # 5 minutes
    )


@router.post(
    "/telegram/verify",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def verify_telegram_code(
    request: Request,
    verify_request: TelegramVerifyRequest,
    user_service: UserService = Depends(get_user_service),
    auth_code_service=Depends(get_telegram_auth_code_service),
):
    """
    Verifica código de autenticación de Telegram.

    Valida el código y retorna tokens JWT si es correcto.

    Args:
        request: Request object
        verify_request: telegram_id y code
        user_service: Servicio de usuarios
        auth_code_service: Servicio de códigos de auth

    Returns:
        AuthResponse: Tokens de acceso

    Raises:
        HTTPException: 401 si el código es inválido
    """
    # Verify code
    is_valid = auth_code_service.verify_code(
        verify_request.telegram_id,
        verify_request.code,
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired code",
        )

    # Get or create user
    user = user_service.get_or_create_by_telegram(
        telegram_id=verify_request.telegram_id,
    )

    # Generate token pair
    access_token, refresh_token = create_token_pair(user.id, user.telegram_id)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
    )
