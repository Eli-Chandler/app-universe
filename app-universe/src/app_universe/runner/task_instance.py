import sqlite3
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import yaml

from app_universe.mcp_server.mcp_server import MCPServerInfo
from app_universe.utils.diff_database import AppUniverseDiff, DatabaseDiff

# TODO: This is a list, because I'm planning on having a public/private data system like appworld for parameterized tasks
def load_task_instances(name: str, tasks_dir: str= ".") -> list["TaskInstance"]:
    task_path = Path(tasks_dir) / name

    # Load metadata from task.yaml
    yaml_path = task_path / "task.yaml"
    with open(yaml_path, 'r') as f:
        metadata = yaml.safe_load(f)

    # Load functions from task.py
    py_path = task_path / "task.py"
    spec = importlib.util.spec_from_file_location("task_module", py_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load task module from {py_path}")

    task_module = importlib.util.module_from_spec(spec)

    sys.modules[f"task_module_{metadata['id']}"] = task_module
    spec.loader.exec_module(task_module)

    # Extract functions
    prepare_data_function = getattr(task_module, "prepare_data")
    evaluate_solution_function = getattr(task_module, "evaluate_solution")
    golden_solution_function = getattr(task_module, "golden_solution", None)

    task_instance = TaskInstance(
        id=metadata["id"],
        name=metadata.get("human_description", metadata["prompt"]),
        prompt=metadata["prompt"],
        prepare_data_function=prepare_data_function,
        evaluate_solution_function=evaluate_solution_function,
        golden_solution_function=golden_solution_function
    )

    return [task_instance]


@dataclass
class TaskInstance:
    id: str
    name: str
    prompt: str
    prepare_data_function: Callable[[dict[str, sqlite3.Connection]], None]
    evaluate_solution_function: Callable[[AppUniverseDiff], bool]
    golden_solution_function: Optional[Callable[[list[MCPServerInfo]], None]] = None
