from abc import ABC, abstractmethod

from app_universe.mcp_server.mcp_server import MCPServerInfo
from app_universe.runner.task_instance import TaskInstance


class BaseAgent(ABC):
    @abstractmethod
    async def run(self, task: TaskInstance, mcp_servers: list[MCPServerInfo]) -> str:
        pass