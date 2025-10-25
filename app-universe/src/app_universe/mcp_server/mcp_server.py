from dataclasses import dataclass
from fastmcp import Client
from loguru import logger

class MCPConnectionError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

# TODO: Extend this to allow protocols other than HTTP

@dataclass(frozen=True)
class MCPServerInfo:
    name: str
    url: str

    @classmethod
    def from_docker_compose(cls, docker_compose: dict) -> list["MCPServerInfo"]:
        mcp_info_list = []
        services = docker_compose.get("services", {})
        for service_name, service_config in services.items():
            ports = service_config.get("ports", [])
            if ports:
                host_port = ports[0].split(":")[0]
                url = f"http://localhost:{host_port}"
                mcp_info_list.append(cls(name=service_name, url=url))
        return mcp_info_list

    def get_client(self) -> Client:
        return Client(self.url)

async def test_mcp_server_connection(mcp_info: MCPServerInfo):
    logger.info(f"Testing connection to MCP server '{mcp_info.name}' at {mcp_info.url}")
    try:
        async with Client(mcp_info.url) as client:
            tools = await client.list_tools()
        logger.info(f"Successfully connected to MCP server '{mcp_info.name}', found {len(tools)} tools.")
    except Exception as e:
        logger.error(f"Failed to connect to MCP server '{mcp_info.name}': {e}")
        raise MCPConnectionError(f"Could not connect to MCP server '{mcp_info.name}' at {mcp_info.url}") from e