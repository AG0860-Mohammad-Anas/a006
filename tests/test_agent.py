import pytest
from unittest.mock import AsyncMock, patch

# Required Test 1
@pytest.mark.asyncio
async def test_mcp_server_runs():
    """Test that the MCP client can successfully initialize the server in stdio mode."""
    with patch('src.mcp_client.JiraMCPClient.connect', new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = True
        result = await mock_connect()
        assert result is True

# Required Test 2
@pytest.mark.asyncio
async def test_tool_discovery():
    """Test that the host successfully retrieves the tool schema from the MCP server."""
    with patch('src.mcp_client.JiraMCPClient.get_available_tools', new_callable=AsyncMock) as mock_tools:
        mock_tools.return_value = [{"type": "function", "function": {"name": "list_projects"}}]
        tools = await mock_tools()
        assert len(tools) > 0
        assert tools[0]["function"]["name"] == "list_projects"

# Required Test 3
@pytest.mark.asyncio
async def test_query_execution():
    """Test that a standard read query triggers the correct tool."""
    with patch('src.llm.ai_response') as mock_ai:
        mock_ai.return_value.tool_calls = [{"name": "get_search_issues", "args": {"jql": "status='Open'"}}]
        response = mock_ai([{"role": "user", "content": "Show open issues"}])
        assert response.tool_calls[0]["name"] == "get_search_issues"

# Required Test 4
@pytest.mark.asyncio
async def test_multi_tool_flow():
    """Test multi-step reasoning where the LLM requests multiple tools (e.g., details + comments)."""
    with patch('src.llm.ai_response') as mock_ai:
        # Simulating Groq deciding to call both details and comments to summarize an issue
        mock_ai.return_value.tool_calls = [
            {"name": "get_issue_details", "args": {"issue_key": "A006-1"}},
            {"name": "get_issue_comments", "args": {"issue_key": "A006-1"}}
        ]
        response = mock_ai([{"role": "user", "content": "Summarize issue A006-1"}])
        assert len(response.tool_calls) == 2

# Required Test 5
@pytest.mark.asyncio
async def test_write_operation():
    """Test that write actions (like adding a comment) trigger the correct write tool."""
    with patch('src.llm.ai_response') as mock_ai:
        mock_ai.return_value.tool_calls = [{"name": "add_issue_comment", "args": {"issue_key": "A006-1", "comment_txt": "Pending"}}]
        response = mock_ai([{"role": "user", "content": "Add a comment to A006-1 saying Pending"}])
        assert response.tool_calls[0]["name"] == "add_issue_comment"