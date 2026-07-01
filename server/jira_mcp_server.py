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
        return response.json()
    except Exception as e:
        return {"error" : f"Jira API call fail{e}"}
    
    
mcp = FastMCP("MCP Host for Jira Issue Assistant")

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


@mcp.tool()
def get_issue_details(id:str) -> str:
    
    return