# A006: MCP Host for Jira Issue Assistant

## 1. Architecture
This project implements an agentic AI workflow combining a **Jira MCP Server** (acting as the data layer) and an **MCP Host** (acting as the orchestrator). 
- The **Server** exposes Jira REST API functions via the FastMCP protocol using `stdio` standard input/output streams.
- The **Host** utilizes the Groq LLM to interpret user prompts, discover available tools, request tool executions, and synthesize the final JSON response containing the `user_query`, `tools_used`, `final_answer`, and `write_action_performed` boolean.

## 2. MCP Server Setup
The server is built using the `fastmcp` Python library. All core functionalities (Read/Write) are wrapped with `@mcp.tool()` decorators. It handles API authentication and simplifies Atlassian Document Format (ADF) payloads to prevent LLM token limits from being exceeded.

## 3. Jira Configuration
To run this project, configure a `.env` file in the root directory:
- `JIRA_BASE_URL`: Your Atlassian domain (e.g., https://yourdomain.atlassian.net/)
- `JIRA_EMAIL`: The email associated with your Jira account.
- `JIRA_API_TOKEN`: Generated from Atlassian Account Security settings.

## 4. Groq Setup
This project utilizes the `llama-3.3-70b-versatile` model via Groq for high-speed function calling. 
Ensure the following are in your `.env`:
- `GROQ_API_KEY`: Your valid Groq API key.
- `GROQ_MODEL`: llama-3.3-70b-versatile

## 5. Running Server (stdio)
The server is designed to be spawned automatically as a background subprocess by the Host. However, it can be tested manually in standard input/output mode using:
```bash
python -m server.jira_mcp_server