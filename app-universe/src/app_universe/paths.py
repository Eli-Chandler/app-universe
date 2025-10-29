import os
from pathlib import Path
from typing import Optional


def find_project_root(marker_file: str = "pyproject.toml") -> Path:
    if os.environ.get("APP_UNIVERSE_ROOT"):
        return Path(os.environ["APP_UNIVERSE_ROOT"]).resolve()

    current = Path(__file__).resolve()

    for parent in current.parents:
        if (parent / marker_file).exists():
            return parent.parent
    
    raise FileNotFoundError(
        f"Could not find project root (searched for {marker_file})"
    )


class ProjectPaths:
    def __init__(self, root: Optional[Path] = None):
        """
        Initialize project paths.
        
        Args:
            root: Project root directory. If None, will be auto-detected.
        """
        self._root = Path(root) if root else find_project_root()
    
    @property
    def root(self) -> Path:
        """Project root directory."""
        return self._root
    
    @property
    def core(self) -> Path:
        """Core framework directory (app-universe/)."""
        return self._root / "app-universe"
    
    @property
    def apps(self) -> Path:
        """Apps directory."""
        return self._root / "apps"
    
    @property
    def data(self) -> Path:
        """Data directory."""
        return self._root / "data"
    
    @property
    def generators(self) -> Path:
        """Generators directory."""
        return self._root / "generators"
    
    @property
    def scripts(self) -> Path:
        """Scripts directory."""
        return self._root / "scripts"
    
    # === Data subdirectories ===
    
    @property
    def world_json(self) -> Path:
        """Path to world.json file."""
        return self.data / "world.json"
    
    @property
    def databases_dir(self) -> Path:
        """Base databases directory."""
        return self.data / "base_databases"
    
    @property
    def tasks_dir(self) -> Path:
        """Tasks directory."""
        return self.data / "tasks"

    def get_database_path(self, app_name: str) -> Path:
        return self.databases_dir / f"{app_name}.db"
    
    def get_task_dir(self, task_id: str) -> Path:
        return self.tasks_dir / task_id
    
    def get_task_yaml(self, task_id: str) -> Path:
        return self.get_task_dir(task_id) / "task.yaml"
    
    def get_task_py(self, task_id: str) -> Path:
        return self.get_task_dir(task_id) / "task.py"
    
    def get_app_dir(self, app_name: str) -> Path:
        return self.apps / app_name
    
    def ensure_exists(self, path: Path, is_dir: bool = True) -> Path:
        if is_dir:
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
        return path


# Global singleton instance
paths = ProjectPaths()


# Convenience functions
def get_project_root() -> Path:
    return paths.root


def get_world_json() -> Path:
    return paths.world_json


def get_database_path(app_name: str) -> Path:
    return paths.get_database_path(app_name)


def get_task_dir(task_id: str) -> Path:
    return paths.get_task_dir(task_id)

