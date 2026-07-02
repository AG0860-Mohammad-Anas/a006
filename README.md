# A006: MCP Host for Jira Issue Assistant

An MCP Host that lets a project manager query and update Jira using natural language. A Groq-powered LLM interprets the query, selects the right MCP tool(s) exposed by a self-built Jira MCP Server, and turns tool results into a plain-language answer. The LLM never talks to Jira directly — it only sees tool schemas and tool results.

# Participant Name:
Mohammad Anas

## 1. Architecture

```
User Query
    |
    v
MCP Host (src/host.py)
    |  loads tool schemas, builds conversation, calls Groq
    v
Groq LLM (llama-3.3-70b-versatile)
    |  decides: answer directly, or call a tool
    v
MCP Host relays tool_call over stdio
    |
    v
Jira MCP Server (server/jira_mcp_server.py)  — separate subprocess
    |  translates MCP tool call into Jira REST API v3 call
    v
Jira Cloud REST API
    |
    v
Tool result flows back: MCP Server -> Host -> Groq
    |
    v
Groq produces final natural-language answer
    |
    v
Host wraps everything in FR-7 JSON envelope and returns it
```

Two independent processes:

| Process | File | Responsibility |
|---|---|---|
| MCP Server | `server/jira_mcp_server.py` | Exposes 6 Jira tools over stdio. No Groq knowledge. |
| MCP Host | `src/host.py` | Spawns the server as a subprocess, drives the Groq tool-calling loop, formats output. |

Host and server communicate exclusively through stdin/stdout using the MCP protocol via `fastmcp` — never HTTP between them.

One production detail worth calling out: Atlassian removed the legacy `GET /rest/api/3/search` endpoint (returns HTTP 410). This project uses the current `POST /rest/api/3/search/jql` endpoint.

## 2. Project Structure

```
a006_mcp_host_jira_assistant/
├── README.md
├── requirements.txt
├── pyproject.toml
├── main.py
├── config.py
├── .env.example
├── sample_queries.md
├── server/
│   └── jira_mcp_server.py    
├── src/
│   ├── host.py                
│   ├── llm.py                
│   ├── mcp_client.py          
│   └── prompts.py            
├── tests/
│   ├── test_mcp_server_runs.py
│   ├── test_tool_discovery.py
│   ├── test_query_execution.py
│   ├── test_multi_tool_flow.py
│   └── test_write_operation.py
└── outputs/                   Query results saved here at runtime
```

## 3. Setup

### 3.1 Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  
pip install -r requirements.txt
```

### 3.2 Configure environment variables

```bash
cp .env.example .env
```

Fill in `.env`:

```
GROQ_API_KEY=<your groq api key>
GROQ_MODEL=llama-3.3-70b-versatile
JIRA_BASE_URL=https://<your-site>.atlassian.net
JIRA_EMAIL=<your atlassian account email>
JIRA_API_TOKEN=<your atlassian api token>
```

### 3.3 Create dummy Jira issues

In your Jira instance, create a handful of issues with varied priority, status, issue type, and assignee so the sample queries below have real data to return. At minimum:

- 2-3 bugs, at least one marked High/Urgent priority and unresolved
- 1-2 issues assigned to you
- 1 issue with an existing comment, to test `get_issue_comments`

## 4. Running the Jira MCP Server (stdio mode)

The server can be run standalone to confirm it starts:

```bash
python server/jira_mcp_server.py
```

It waits for MCP protocol messages on stdin. In normal usage you do not run this manually — `src/host.py` spawns it as a subprocess automatically.

## 5. Running the MCP Host

```bash
python main.py
```

Or directly:

```bash
python src/host.py
```

This starts an interactive prompt:

```
you> Show all open high-priority issues.
{
  "user_query": "Show all open high-priority issues.",
  "tools_used": ["search_issues"],
  "final_answer": "...",
  "write_action_performed": false
}
```

Type `exit` or `quit` to stop. Each result is also saved to `outputs/`.

## 6. Running tests

```bash
pytest -v
```

`test_mcp_server_runs` and `test_tool_discovery` spawn the real server subprocess over stdio (Jira calls are not exercised — they only verify the MCP transport and tool schemas). The remaining tests inject fake Groq and MCP clients so the orchestration logic in `host.py` is tested deterministically without live network calls.

## 7. Sample Queries

See `sample_queries.md` for the full list with expected tool usage.

## 8. Output Format (FR-7)

Every query returns:

```json
{
  "user_query": "string",
  "tools_used": ["tool_name"],
  "final_answer": "string",
  "write_action_performed": false
}
```

`write_action_performed` is `true` whenever `add_issue_comment` or `update_issue_status` appears in `tools_used`.

## 9. Known Constraints

- `update_issue_status` moves an issue along its existing workflow transitions. It returns a clear error listing valid transitions if the requested status is not reachable.
- `search_issues` caps `max_results` at 100 per call and does not paginate. The default is controlled by `JIRA_DEFAULT_MAX_RESULTS` in `.env`.
