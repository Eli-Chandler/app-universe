from abc import ABC, abstractmethod

from abc import ABC, abstractmethod

from app_universe.mcp_server.mcp_server import MCPServerInfo


class EnvironmentPreparer(ABC):
    async def __aenter__(self) -> list[MCPServerInfo]:
        return await self.setup()


    async def __aexit__(self, exc_type, exc, tb):
        await self.teardown()

    @abstractmethod
    async def setup(self) -> list[MCPServerInfo]:
        pass

    @abstractmethod
    async def teardown(self):
        pass
