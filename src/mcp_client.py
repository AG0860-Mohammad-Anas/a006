import asyncio
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

class JiraMCPClient:
    def __init__(self):
        self.session = None
        self.exit_stack = None

    async def connect(self):
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "server.jira_mcp_server"]
        )
        
        from contextlib import AsyncExitStack
        self.exit_stack = AsyncExitStack()
        
        read_stream, write_stream = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        
        await self.session.initialize()
        print("✅ Successfully connected to Jira MCP Server!")

    async def get_available_tools(self) -> list:
        
        if not self.session:
            raise RuntimeError("Not connected to MCP server.")
            
        response = await self.session.list_tools()
        
        formatted_tools = []
        for tool in response.tools:
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
            
        return formatted_tools

    async def call_tool(self, tool_name: str, tool_args: dict) -> str:
        if not self.session:
            raise RuntimeError("Not connected to MCP server.")
            
        try:
            result = await self.session.call_tool(tool_name, tool_args)
            
            if result.content and len(result.content) > 0:
                return result.content[0].text
            return "Success (No content returned)"
            
        except Exception as e:
            return f"Tool execution failed: {str(e)}"

    async def disconnect(self):
        if self.exit_stack:
            await self.exit_stack.aclose()
            

# --- Temporary Test Block ---
if __name__ == "__main__":
    async def test_client():
        client = JiraMCPClient()
        await client.connect()
        tools = await client.get_available_tools()
        print(f"Found {len(tools)} tools: {[t['function']['name'] for t in tools]}")
        await client.disconnect()
        
    asyncio.run(test_client())