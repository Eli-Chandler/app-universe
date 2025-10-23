from abc import ABC, abstractmethod

from app_universe.mcp_server.mcp_server import MCPServerInfo


class BaseAgent(ABC):
    @abstractmethod
    async def run(self, prompt: str, mcp_servers: list[MCPServerInfo]) -> str:
        pass