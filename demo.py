from app_universe.app_agents.gold_solution_agent import GoldSolutionAgent
# from app_universe.app_agents.react_agent import ReActAgent
import docker

from app_universe.runner.environment_preparer import DockerEnvironmentPreparer
from app_universe.runner.runner import TaskRunner
from app_universe.runner.task_instance import load_task_instances


task = load_task_instances("no-op-task", tasks_dir="data/tasks")[0]

docker_client = docker.DockerClient()
environment_preparer = DockerEnvironmentPreparer(docker_client, image_tags={"gmail": "app-universe-gmail:latest"})
base_db_paths = {"gmail": "data/base_databases/gmail.db"}
task_runner = TaskRunner(task, base_db_paths, environment_preparer)

if task.golden_solution_function is None:
    raise ValueError("The task does not have a golden solution function defined.")

agent = GoldSolutionAgent(task.golden_solution_function)

async def run_task():
    result = await task_runner.run(agent)
    print(f"Task result: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_task())