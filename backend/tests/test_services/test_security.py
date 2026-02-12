from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    decrypt_token,
    encrypt_token,
)


def test_access_and_refresh_tokens_encode_decode():
    access = create_access_token("user-123")
    refresh = create_refresh_token("user-123")

    access_payload = decode_token(access)
    refresh_payload = decode_token(refresh)

    assert access_payload["sub"] == "user-123"
    assert access_payload["type"] == "access"
    assert refresh_payload["sub"] == "user-123"
    assert refresh_payload["type"] == "refresh"


def test_encrypt_decrypt_roundtrip():
    raw = "gho_test_token_value"
    encrypted = encrypt_token(raw)
    decrypted = decrypt_token(encrypted)

    assert encrypted != raw
    assert decrypted == raw
