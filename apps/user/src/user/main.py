from fastmcp import FastMCP, Context
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token


JWT_SECRET = "app-universe-very-secret-key"

verifier = JWTVerifier(
    public_key=JWT_SECRET, algorithm="HS256"
)

mcp = FastMCP(name="User Info", auth=verifier)

@mcp.tool
def get_user_info(ctx: Context) -> dict:
    token = get_access_token()
    return token
