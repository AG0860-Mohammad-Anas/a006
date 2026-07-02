from fastmcp import FastMCP
import requests
import json
from config import JIRA_BASE_URL,JIRA_EMAIL,JIRA_API_TOKEN 
from requests.auth import HTTPBasicAuth


def make_jira_req(method,endpoint,payload=None):
    """Generating the base header for accesssing the JIRA API"""
    url = f"{JIRA_BASE_URL.strip('/')}{endpoint}"
    
    auth = HTTPBasicAuth(JIRA_EMAIL,JIRA_API_TOKEN)
    
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json"
    }
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers,auth=auth)
        elif method.upper() == "POST":
            response = requests.post(url,headers=headers,auth=auth,json=payload)
        elif method.upper() == "PUT":
            response = requests.put(url,auth=auth,headers=headers,json=payload)
             
        response.raise_for_status()
        if not response.text:
            return {"success": True}
        return response.json()
    except Exception as e:
        return {"error" : f"Jira API call fail{e}"}
    
    
mcp = FastMCP("MCP Host for Jira Issue Assistant")
#1
@mcp.tool()
def get_list_projects() -> str:
    """get all the listed Jira projects"""
    data = make_jira_req("GET","/rest/api/3/project")
    simplified_output = [
        {
            "name":project.get("name"), "key" : project.get("key")
        }
        for project in data
    ]
    return json.dumps(simplified_output,indent=2)
#2
@mcp.tool()
def get_search_issues(jql:str) -> str:
    """Search for Jira issues using a JQL (Jira Query Language) string.
    Use this tool whenever the user asks to find, list, or filter issues."""
    
    payload = {
        "jql" : jql,
        "maxResults" : 10
    }
    
    data = make_jira_req(method="POST",endpoint="/rest/api/3/search/jql",payload=payload)
    
    if "error" in data:
        return data
    
    return data

#3
@mcp.tool()
def get_issue_details(issue_key:str) -> str:
    """
    Get the specific details of a single Jira issue by its key (e.g., A006-3).
    Use this when you need to summarize an issue or find out who is assigned to it.
    """
    data = make_jira_req("GET",endpoint=f"/rest/api/3/issue/{issue_key}")
    if "error" in data:
        return json.dumps(data)
    
    fields = data.get("fields",{})
    
    simplified_issue = {
        "key" : data.get("key"),
        "summary" : fields.get("summary"),
        "description" : fields.get("description"),
        "status": fields.get("status", {}).get("name") if fields.get("status") else None,
        "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
        "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else "Unassigned",
        "reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else "Unknown"
    }
    
    return json.dumps(simplified_issue,indent=2)
#4
@mcp.tool()
def get_issue_comments(issue_key:str)->str:
    """
    Get the comments of a single Jira issue by its key (e.g., A006-2).
    Use this to see the conversation history or get updates on an issue.
    """
    
    data = make_jira_req("GET",endpoint=f"/rest/api/3/issue/{issue_key}/comment")
    if "error" in data:
        return json.dumps(data)
    
    raw_comments = data.get("comments",[])
    simplified_comments = []
    
    for comment in raw_comments:
        author = comment.get("author", {}).get("displayName", "Unknown")
        
        text_snippets = []
        
        for block in comment.get("body",{}).get("content",[]):
            for node in block.get("content",[]):
                if node.get("type") == "text":
                    text_snippets.append(node.get("text",""))
        full_txt = " ".join(text_snippets)
        simplified_comments.append(
            {
                "author":author,
                "text":full_txt
            }
        )
    return json.dumps(simplified_comments, indent=2)

#5
@mcp.tool()
def add_issue_comment(issue_key:str,comment_txt:str)->str:
    """
    """
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "text": comment_txt,
                            "type": "text"
                        }
                    ]
                }
            ]
        }
    }
    try:
        data = make_jira_req("POST",endpoint=f"/est/api/3/issue/{issue_key}/comment",payload=payload)
        return f"Successfully added comment to {issue_key}" 
    except Exception as e:
        return f"errror {e}"

#6
@mcp.tool()
def update_issue_status(issue_key: str, status_name: str) -> str:
    """
    Update the status of a Jira issue (e.g., to 'In Progress', 'Done', 'To Do').
    Use this when the user asks to move, close, or update the status of a ticket.
    """
    transitions_data = make_jira_req("GET", f"/rest/api/3/issue/{issue_key}/transitions")
    
    if "error" in transitions_data:
        return str(transitions_data)

    available_transitions = transitions_data.get("transitions", [])
    
    transition_id = None
    available_names = []
    
    for t in available_transitions:
        t_name = t.get("name", "")
        to_status = t.get("to", {}).get("name", "")
        available_names.append(to_status)
        
        if status_name.lower() in t_name.lower() or status_name.lower() in to_status.lower():
            transition_id = t.get("id")
            break
            
    if not transition_id:
        return f"Error: Cannot move to '{status_name}'. Valid statuses for this issue are: {', '.join(available_names)}"

    payload = {
        "transition": {
            "id": transition_id
        }
    }
    
    update_response = make_jira_req("POST", f"/rest/api/3/issue/{issue_key}/transitions", payload=payload)
    
    if "error" in update_response and "JSONDecodeError" not in str(update_response):
         return str(update_response)
         
    return f"Successfully updated {issue_key} to '{status_name}'." 