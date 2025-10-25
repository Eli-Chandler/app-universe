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


    async def run(self, prompt: str, mcp_servers: list[MCPServerInfo]) -> str:
        client = MultiServerMCPClient(
            {
                mcp_info.name: {"url": mcp_info.url, "transport": "streamable_http"}
                for mcp_info in mcp_servers
            }
        )
        tools = await client.get_tools()
        agent = create_agent(self._model, tools, response_format=ResponseFormat)

        result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]}, config={"callbacks": [FunctionCallbackHandler(logger.info)]})
        rf: ResponseFormat = result['structured_response']
        logger.info(f"Agent completed with summary/answer: {rf.summary_or_answer}")
        return rf.summary_or_answer