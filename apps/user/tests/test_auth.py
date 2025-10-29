# tests/test_auth_jwt.py
import datetime as dt
from fastmcp.client import BearerAuth
import pytest
import jwt

from fastmcp import Client
from fastmcp.utilities.tests import run_server_async


from user.main import mcp


@pytest.mark.asyncio
async def test_auth_with_hs256_jwt():
    # Match your verifier secret and give standard JWT claims
    secret = "app-universe-very-secret-key"
    now = dt.datetime.now(dt.timezone.utc)

    token = jwt.encode(
        {
            "sub": "test-user-123",
            "iss": "internal-auth-service",
            "aud": "user-info-api",     # verifier in your snippet doesn't check aud/iss,
            "iat": int(now.timestamp()),# but including them is good practice
            "exp": int((now + dt.timedelta(minutes=10)).timestamp()),
            "scope": "read:userinfo",
        },
        key=secret,
        algorithm="HS256",
    )

    # Run the FastMCP server locally over HTTP and call the tool with the token
    async with run_server_async(mcp, transport="http") as url:
        async with Client(url, auth=BearerAuth(token)) as client:
            result = await client.call_tool(name="get_user_info", arguments={})

    # Your get_user_info returns get_access_token() -> AccessToken (JSON-serializable)
    print(result)
    assert result.data is not None
    # AccessToken includes standard fields + claims (subject/claims in newer versions)
    # Prefer robust checks so test passes across minor versions:
    subject = (
        result.data.get("subject")
        or result.data.get("sub")                   # older shapes
        or (result.data.get("claims") or {}).get("sub")
    )
    assert subject == "test-user-123"
