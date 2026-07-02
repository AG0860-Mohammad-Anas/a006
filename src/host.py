import json
from pathlib import Path
from datetime import datetime
from src.mcp_client import JiraMCPClient
from src.llm import ai_response

async def run_agent(user_query: str):
    client = JiraMCPClient()

    tools_used = []
    write_action_performed = False
    write_tools = ["add_issue_comment", "update_issue_status"]

    try:
        await client.connect()
        mcp_tools = await client.get_available_tools()

        messages = [{"role": "user", "content": user_query}]
        print(f"\n Processing query: '{user_query}'...")

        while True:
            response_msg = ai_response(messages, tools=mcp_tools)

            messages.append(response_msg)

            if not response_msg.tool_calls:
                final_answer = response_msg.content
                break

            for tool_call in response_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                print(f"LLM requested tool: {tool_name}")

                tools_used.append(tool_name)
                if tool_name in write_tools:
                    write_action_performed = True

                result_content = await client.call_tool(tool_name, tool_args)

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

    output = {
        "user_query": user_query,
        "tools_used": list(set(tools_used)), # Remove duplicates
        "final_answer": final_answer,
        "write_action_performed": write_action_performed,
    }

    print("\n" + "=" * 50)
    print(json.dumps(output, indent=2))
    print("=" * 50)

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"jira_response_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)
        
    print(f"\n Output saved to: {output_file}\n")
    return output