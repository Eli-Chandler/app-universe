import sqlite3

from app_universe.runner.database_sandbox import DatabaseSandbox
from app_universe.runner.environment_preparer import EnvironmentPreparer
from loguru import logger

from app_universe.app_agents.base import BaseAgent
from app_universe.mcp_server.mcp_server import MCPServerInfo
from app_universe.runner.task_instance import TaskInstance
from app_universe.utils.diff_database import AppUniverseDiff, DatabaseDiff, diff_databases


class TaskRunner:
    def __init__(self, task: TaskInstance, base_db_paths: dict[str, str], environment_preparer: EnvironmentPreparer):
        self._task = task
        self._environment_preparer = environment_preparer
        self._base_db_paths = base_db_paths

        self._base_db_connections: dict[str, sqlite3.Connection] = {
            db_name: sqlite3.connect(db_path)
            for db_name, db_path in base_db_paths.items()
        }

    def _prepare_databases(self, temp_db_connections: dict[str, sqlite3.Connection]) -> None:
        self._task.prepare_data_function(temp_db_connections)

    async def _run_agent(self, agent: BaseAgent, mcp_servers: list[MCPServerInfo]) -> str:
        return await agent.run(self._task.prompt, mcp_servers)

    def _diff_databases(self, temp_db_connections: dict[str, sqlite3.Connection]) -> AppUniverseDiff:
        return diff_databases(self._base_db_connections, temp_db_connections)

    def _evaluate_solution(self, database_diffs: AppUniverseDiff) -> bool:
        return self._task.evaluate_solution_function(database_diffs)

    async def run(self, agent: BaseAgent) -> bool:
        sandbox = DatabaseSandbox(self._base_db_paths)
        with sandbox.session() as sb:
            logger.info(f"Starting task runner for task: {self._task.name}")

            logger.info(f"Preparing databases for task: {self._task.name}")
            self._prepare_databases(sb.conns)

            logger.info(f"Preparing environment for task: {self._task.name}")
            async with self._environment_preparer.prepare(sb.paths) as mcp_servers:
                logger.info(f"Running agent for task: {self._task.name}")
                await self._run_agent(agent, mcp_servers)

                logger.info(f"Tearing down environment for task: {self._task.name}")

            logger.info(f"Diffing databases for task: {self._task.name}")
            diffs = self._diff_databases(sb.conns)

            logger.info(f"Evaluating solution for task: {self._task.name}")
            result = self._evaluate_solution(diffs)

            return result
