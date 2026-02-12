import secrets

from app.core.security import create_access_token, create_refresh_token, decode_token


class AuthService:
    @staticmethod
    def generate_state() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_tokens(subject: str) -> dict[str, str]:
        return {
            "access_token": create_access_token(subject),
            "refresh_token": create_refresh_token(subject),
            "token_type": "bearer",
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        subject = payload.get("sub")
        if not subject:
            raise ValueError("Invalid refresh token subject")
        return create_access_token(subject)
