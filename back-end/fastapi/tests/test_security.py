from app.security import hash_password, verify_password, hash_refresh_token, new_refresh_token, sign_access_token, verify_access_token
def test_password_hashing_round_trip():
    encoded = hash_password("correct-horse-battery-staple")
    assert encoded != "correct-horse-battery-staple"
    assert verify_password("correct-horse-battery-staple", encoded)
    assert not verify_password("wrong-password", encoded)
def test_refresh_tokens_are_random_and_hashed():
    first, second = new_refresh_token(), new_refresh_token()
    assert first != second
    assert hash_refresh_token(first) != first
    assert hash_refresh_token(first) == hash_refresh_token(first)
def test_access_token_round_trip():
    assert verify_access_token(sign_access_token("user-123"))["sub"] == "user-123"
