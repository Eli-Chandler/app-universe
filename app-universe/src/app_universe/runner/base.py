from abc import ABC, abstractmethod
from dataclasses import dataclass
import sqlite3
from typing import Callable

from app_universe.app_agents.base import BaseAgent
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

class TaskRunner(ABC):
    def __init__(self, task: Task):
        self._task = task

    def _prepare_databases(self):
        self._task.prepare_data_function(self._task.db_connections)

    @abstractmethod
    def _prepare_environment(self):
        pass


    def _run_agent(self, agent: BaseAgent):
        pass

    def _diff_databases(self) -> dict[str, DatabaseDiff]:
        return {
            db_name: diff_databases(self._task.base_db_connections[db_name], self._task.db_connections[db_name])
            for db_name in self._task.db_connections
        }

    def _evaluate_solution(self, database_diffs: dict[str, DatabaseDiff]) -> bool:
        return self._task.evaluate_solution_function(database_diffs)

    def run(self, agent: BaseAgent) -> bool:
        self._prepare_databases()
        self._prepare_environment()
        self._run_agent(agent)
        diffs = self._diff_databases()
        return self._evaluate_solution(diffs)