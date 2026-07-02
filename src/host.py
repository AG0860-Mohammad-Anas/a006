import asyncio
import json
from src.mcp_client import JiraMCPClient
from llm import ai_response

async def run_agent(user_query: str):
    client = JiraMCPClient()
    
    # Variables to track for the FR-7 Output Requirement
    tools_used = []
    write_action_performed = False
    write_tools = ["add_issue_comment", "update_issue_status"]

    try:
        # 1. Connect and get tools
        await client.connect()
        mcp_tools = await client.get_available_tools()
        
        # 2. Setup Conversation History
        messages = [{"role": "user", "content": user_query}]
        
        print(f"\n🧠 Processing query: '{user_query}'...")
        
        # 3. The Agentic Loop (Handles Multi-Step Reasoning - FR-5)
        while True:
            # Ask Groq what to do next
            response_msg = ai_response(messages, tools=mcp_tools)
            
            # Append Groq's response to the history so it remembers its own thoughts
            messages.append(response_msg)
            
            # If Groq didn't want to use any tools, it means it generated the final text answer!
            if not response_msg.tool_calls:
                final_answer = response_msg.content
                break
                
            # If Groq DID want to use tools, we execute them
            for tool_call in response_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                print(f"🛠️  LLM requested tool: {tool_name}")
                
                # Track for FR-7 requirements
                tools_used.append(tool_name)
                if tool_name in write_tools:
                    write_action_performed = True
                
                # Execute the tool on the MCP Server
                result_content = await client.call_tool(tool_name, tool_args)
                
                # Append the tool's result back to the conversation history
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_name,
                    "content": str(result_content)
                })
                
    except Exception as e:
        final_answer = f"An error occurred: {e}"
        
    finally:
        await client.disconnect()

    # 4. Format Output strictly to FR-7 Requirements
    output = {
        "user_query": user_query,
        "tools_used": list(set(tools_used)), # Remove duplicates if a tool was called twice
        "final_answer": final_answer,
        "write_action_performed": write_action_performed
    }
    
    # Print the final result beautifully
    print("\n" + "="*50)
    print(json.dumps(output, indent=2))
    print("="*50 + "\n")

if __name__ == "__main__":
    # Test your first query! 
    # Make sure your Jira dummy data has at least one open issue.
    query = "Show me all open high-priority issues."
    asyncio.run(run_agent(query))