import sqlite3
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from fastmcp import Client
import yaml

from app_universe.utils.diff_database import AppUniverseDiff
from app_universe.paths import paths

# TODO: This is a list, because I'm planning on having a public/private data system like appworld for parameterized tasks
def load_task_instances(name: str, tasks_dir: str = None) -> list["TaskInstance"]:
    # Use default tasks directory if not specified
    if tasks_dir is None:
        task_path = paths.get_task_dir(name)
    else:
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
        user_id=metadata["user_id"],
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
    user_id: int
    prepare_data_function: Callable[[dict[str, sqlite3.Connection]], None]
    evaluate_solution_function: Callable[[AppUniverseDiff], bool]
    golden_solution_function: Callable[[str, dict[str, Client]], str] | None = None
