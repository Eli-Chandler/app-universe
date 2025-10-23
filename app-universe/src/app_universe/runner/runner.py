from dataclasses import dataclass
import sqlite3
from typing import Callable
from app_universe.runner.environment_preparer import EnvironmentPreparer
from loguru import logger

from app_universe.app_agents.base import BaseAgent
from app_universe.mcp_server.mcp_server import MCPServerInfo
from app_universe.utils.diff_database import DatabaseDiff, diff_databases



@dataclass
class Task:
    id: str
    name: str
    prompt: str
    prepare_data_function: Callable[[dict[str, sqlite3.Connection]], None]
    evaluate_solution_function: Callable[[dict[str, DatabaseDiff]], bool]
    base_db_connections: dict[str, sqlite3.Connection]
    db_connections: dict[str, sqlite3.Connection]

class TaskRunner:
    def __init__(self, task: Task, environment_preparer: EnvironmentPreparer):
        self._task = task
        self._environment_preparer = environment_preparer

    def _prepare_databases(self):
        self._task.prepare_data_function(self._task.db_connections)

    async def _run_agent(self, agent: BaseAgent, mcp_servers: list[MCPServerInfo]) -> str:
        return await agent.run(self._task.prompt, mcp_servers)

    def _diff_databases(self) -> dict[str, DatabaseDiff]:
        return {
            db_name: diff_databases(self._task.base_db_connections[db_name], self._task.db_connections[db_name])
            for db_name in self._task.db_connections
        }

    def _evaluate_solution(self, database_diffs: dict[str, DatabaseDiff]) -> bool:
        return self._task.evaluate_solution_function(database_diffs)

    async def run(self, agent: BaseAgent) -> bool:
        logger.info(f"Starting task runner for task: {self._task.name}")

        logger.info(f"Preparing databases for task: {self._task.name}")
        self._prepare_databases()

        logger.info(f"Preparing environment for task: {self._task.name}")
        async with self._environment_preparer as mcp_servers:
            logger.info(f"Running agent for task: {self._task.name}")
            await self._run_agent(agent, mcp_servers)

            logger.info(f"Tearing down environment for task: {self._task.name}")

        logger.info(f"Diffing databases for task: {self._task.name}")
        diffs = self._diff_databases()

        logger.info(f"Evaluating solution for task: {self._task.name}")
        return self._evaluate_solution(diffs)
