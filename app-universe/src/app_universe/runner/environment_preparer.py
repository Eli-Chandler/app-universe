from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
import asyncio

from app_universe.mcp_server.mcp_server import MCPServerInfo, test_mcp_server_connection

from docker import DockerClient
from loguru import logger

class EnvironmentPreparer(ABC):
    @asynccontextmanager
    async def prepare(self, temp_db_paths: dict[str, str]):
        mcp_servers = await self.setup(temp_db_paths)
        try:
            yield mcp_servers
        finally:
            await self.teardown(temp_db_paths)

    @abstractmethod
    async def setup(self, temp_db_paths: dict[str, str]) -> list[MCPServerInfo]:
        pass

    @abstractmethod
    async def teardown(self, temp_db_paths: dict[str, str]):
        pass

DOCKER_MCP_PORT = 9000
DOCKER_DB_ENV_VAR = 'DATABASE_URL'


class DockerEnvironmentPreparer(EnvironmentPreparer):
    def __init__(self, docker_client: DockerClient, image_tags: dict[str, str]):
        self._docker_client = docker_client
        self._image_tags = image_tags
        self._containers = []

    async def setup(self, temp_db_paths: dict[str, str]) -> list[MCPServerInfo]:
        mcp_servers = []

        for app_name, db_path in temp_db_paths.items():
            if app_name not in self._image_tags:
                raise ValueError(f"No image tag found for app '{app_name}'")

            image_tag = self._image_tags[app_name]

            # Create and start container
            container = self._docker_client.containers.run(
                image_tag,
                detach=True,
                environment={
                    DOCKER_DB_ENV_VAR: 'sqlite:////data/database.db'
                },
                volumes={
                    db_path: {'bind': '/data/database.db', 'mode': 'rw'}
                },
                ports={f'{DOCKER_MCP_PORT}/tcp': None},  # Auto-assign host port
                name=f"{app_name}-{id(self)}",
                remove=False
            )

            self._containers.append(container)

            # Get the assigned port
            container.reload()
            port_bindings = container.attrs['NetworkSettings']['Ports']
            host_port = port_bindings[f'{DOCKER_MCP_PORT}/tcp'][0]['HostPort']

            # Create MCP server info
            mcp_info = MCPServerInfo(
                name=app_name,
                url=f"http://localhost:{host_port}/mcp"
            )
            mcp_servers.append(mcp_info)

        # Wait for all MCP servers to be ready
        logger.info("Waiting for MCP servers to be ready...")
        for mcp_info in mcp_servers:
            max_retries = 30
            retry_delay = 1  # seconds

            for attempt in range(max_retries):
                try:
                    await test_mcp_server_connection(mcp_info)
                    break
                except Exception:
                    if attempt < max_retries - 1:
                        logger.debug(f"MCP server '{mcp_info.name}' not ready yet (attempt {attempt + 1}/{max_retries}), retrying...")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"MCP server '{mcp_info.name}' failed to become ready after {max_retries} attempts")
                        raise

        return mcp_servers

    async def teardown(self, temp_db_paths: dict[str, str]):
        for container in self._containers:
            try:
                container.stop(timeout=5)
                container.remove()
            except Exception as e:
                # Log but continue teardown
                logger.error(f"Error stopping container {container.name}: {e}")

        self._containers = []
