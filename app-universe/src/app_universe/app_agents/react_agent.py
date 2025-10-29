from app_universe.runner.task_instance import TaskInstance
from app_universe.world.auth import user_id_to_jwt
from langchain.agents import create_agent
from langchain_core.tracers.stdout import FunctionCallbackHandler

from app_universe.app_agents.base import BaseAgent


from app_universe.mcp_server.mcp_server import MCPServerInfo
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel
from loguru import logger

class ResponseFormat(BaseModel):
    summary_or_answer: str

class ReActAgent(BaseAgent):
    def __init__(self, model: str = "openai:gpt-5-mini"):
        self._model = model


    async def run(self, task: TaskInstance, mcp_servers: list[MCPServerInfo]) -> str:
        # Since the auth is passed in headers
        # The agent doesn't have to worry about it
        # Only reason I use JWT is because passing user info in other ways e.g. basic would be messy
        # Wanted something standardised

        client = MultiServerMCPClient(
            {
                mcp_info.name: {"url": mcp_info.url, "transport": "streamable_http", "headers": {"Authorization": f"Bearer {user_id_to_jwt(task.user_id)}"}}
                for mcp_info in mcp_servers
            }
        )
        tools = await client.get_tools()
        agent = create_agent(self._model, tools, response_format=ResponseFormat)

        result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]}, config={"callbacks": [FunctionCallbackHandler(logger.info)]})
        rf: ResponseFormat = result['structured_response']
        logger.info(f"Agent completed with summary/answer: {rf.summary_or_answer}")
        return rf.summary_or_answer