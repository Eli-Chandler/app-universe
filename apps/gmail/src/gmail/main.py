from fastmcp import FastMCP

mcp = FastMCP("GMail")

@mcp.tool
def read_email() -> list[str]:
    return ["Email 1", "Email 2", "Email 3"]

if __name__ == "__main__":
    mcp.run()