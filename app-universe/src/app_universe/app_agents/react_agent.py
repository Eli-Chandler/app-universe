import asyncio

from langchain.agents import create_agent

from app_universe.app_agents.base import BaseAgent


from app_universe.mcp_server.mcp_server import MCPServerInfo
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel

class ResponseFormat(BaseModel):
    summary_or_answer: str

class ReActAgent(BaseAgent):
    def __init__(self, mcp_info_list: list[MCPServerInfo], model: str = "openai:gpt-5-mini"):
        self._client = MultiServerMCPClient(
            {
                mcp_info.name: {
                    "url": mcp_info.url, "transport": "streamable_http"
                }
                for mcp_info in mcp_info_list
            }
        )
        self._model = model


    async def run(self, prompt: str) -> str:
        tools = await self._client.get_tools()
        agent = create_agent(self._model, tools, response_format=ResponseFormat)
        result = await agent.ainvoke({"messages": [{"role": "user", "content": "Whats in my email?"}]})
        rf: ResponseFormat = result['structured_response']
        return rf.summary_or_answer