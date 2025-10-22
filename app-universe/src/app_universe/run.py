import asyncio
from app_universe.app_agents.react_agent import ReActAgent
from app_universe.mcp_server.mcp_server import MCPServerInfo, test_mcp_server_connection
from loguru import logger

async def run_agent(mcp_info_list: list[MCPServerInfo], task: str):
    for mcp_info in mcp_info_list:
        await test_mcp_server_connection(mcp_info)

    agent = ReActAgent(mcp_info_list)
    logger.info(f"Running agent for task: {task}")
    result = await agent.run(task)
    print("Agent Result:", result)


async def main():
    await run_agent([
        MCPServerInfo(
            name="gmail",
            url="http://localhost:9001/mcp",
        )],
        "Check my email"
    )

if __name__ == '__main__':
    asyncio.run(main())