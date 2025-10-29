import jwt

# This is not a secret
# The LLM doesn't even see the token, so this doesn't matter
JWT_SECRET = "app-universe-very-secret-key"

def user_id_to_jwt(user_id: int) -> str:
    payload = {
        "user_id": user_id
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token
