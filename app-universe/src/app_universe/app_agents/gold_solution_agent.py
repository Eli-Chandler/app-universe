from typing import Callable

from app_universe.app_agents.base import BaseAgent
from fastmcp import Client

from app_universe.mcp_server.mcp_server import MCPServerInfo


class GoldSolutionAgent(BaseAgent):
    def __init__(self, golden_solution_function: Callable[[str, dict[str, Client]], str]):
        self._golden_solution_function = golden_solution_function

    async def run(self, prompt: str, mcp_servers: list[MCPServerInfo]) -> str:
        mcp_clients = {server.name: server.get_client() for server in mcp_servers}
        return self._golden_solution_function(prompt, mcp_clients)
