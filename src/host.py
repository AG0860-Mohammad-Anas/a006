import json
from pathlib import Path
from datetime import datetime

from src.mcp_client import JiraMCPClient
from src.llm import ai_response


async def run_agent(user_query: str):
    client = JiraMCPClient()

    tools_used = []
    write_action_performed = False

    try:
        # Connect to MCP Server
        await client.connect()

        query = user_query.lower().strip()

        print(f"\n🧠 Processing query: '{user_query}'...")

        # =====================================================
        # Manual routing for common Jira queries
        # =====================================================

        if "project" in query:
            tools_used.append("list_projects")
            final_answer = await client.call_tool(
                "list_projects",
                {}
            )

        elif "high" in query and "priority" in query:
            tools_used.append("search_issues")
            final_answer = await client.call_tool(
                "search_issues",
                {
                    "jql": "priority = High"
                }
            )

        elif "open" in query:
            tools_used.append("search_issues")
            final_answer = await client.call_tool(
                "search_issues",
                {
                    "jql": 'status = "To Do" OR status = Open'
                }
            )

        elif "assigned" in query:
            tools_used.append("search_issues")
            final_answer = await client.call_tool(
                "search_issues",
                {
                    "jql": "assignee=currentUser()"
                }
            )

        elif "comment" in query and "add" in query:
            import re

            match = re.search(
                r"([A-Z0-9]+-\d+)",
                user_query,
                re.IGNORECASE
            )

            if match:
                issue_key = match.group(1)

                comment = user_query.split(issue_key)[-1].replace(
                    "add",
                    ""
                ).replace(
                    "comment",
                    ""
                ).strip()

                tools_used.append("add_issue_comment")
                write_action_performed = True

                final_answer = await client.call_tool(
                    "add_issue_comment",
                    {
                        "issue_key": issue_key,
                        "comment_txt": comment,
                    },
                )
            else:
                final_answer = "Issue key not found."

        elif "status" in query or "move" in query:

            import re

            match = re.search(r"([A-Z]+-\d+)", user_query)

            if match:

                issue_key = match.group(1)

                if "done" in query:
                    status = "Done"
                elif "progress" in query:
                    status = "In Progress"
                else:
                    status = "To Do"

                tools_used.append("update_issue_status")
                write_action_performed = True

                final_answer = await client.call_tool(
                    "update_issue_status",
                    {
                        "issue_key": issue_key,
                        "status_name": status,
                    },
                )

            else:
                final_answer = "Issue key not found."

        elif "summary" in query or "summarize" in query:

            import re

            match = re.search(r"([A-Z]+-\d+)", user_query)

            if match:

                issue_key = match.group(1)

                tools_used.append("get_issue_details")

                final_answer = await client.call_tool(
                    "get_issue_details",
                    {
                        "issue_key": issue_key,
                    },
                )

            else:
                final_answer = "Issue key not found."

        elif "comments" in query:

            import re

            match = re.search(r"([A-Z]+-\d+)", user_query)

            if match:

                issue_key = match.group(1)

                tools_used.append("get_issue_comments")

                final_answer = await client.call_tool(
                    "get_issue_comments",
                    {
                        "issue_key": issue_key,
                    },
                )

            else:
                final_answer = "Issue key not found."

        # =====================================================
        # Fallback to Groq
        # =====================================================

        else:

            print("🤖 Using Groq reasoning...")

            response = ai_response(
                [
                    {
                        "role": "user",
                        "content": user_query,
                    }
                ]
            )

            if hasattr(response, "content"):
                final_answer = response.content
            else:
                final_answer = str(response)

    except Exception as e:

        final_answer = f"An error occurred: {e}"

    finally:

        await client.disconnect()

    output = {
        "user_query": user_query,
        "tools_used": tools_used,
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

    print(f"\n✅ Output saved to: {output_file}\n")

    return output