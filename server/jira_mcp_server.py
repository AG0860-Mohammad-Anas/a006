from fastmcp import FastMCP
import requests
from config import JIRA_BASE_URL,JIRA_EMAIL,JIRA_API_TOKEN 

# a helper function for calling the JIRA apis securely and increase the modularity of the structure

def make_jira_req(method,endpoint,payload=None):
    """Generating the base header for accesssing the JIRA API"""
    url = f"{JIRA_BASE_URL.strip('/')}{endpoint}"
    
    auth = requests.auth(JIRA_EMAIL,JIRA_API_TOKEN)
    
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json"
    }
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers,auth=auth)
        elif method.upper() == "POST":
            response = requests.get(url,headers=headers,auth=auth,json=payload)
        elif method.upper() == "PUT":
            response = requests.get(url,auth=auth,headers=headers,json=payload)
             
        response.raise_for_status()
        return response.json()
    
    except Exception as e:
        return {"error" : f"Jira API call fail{e}"}
    
    
mcp = FastMCP("MCP Host for Jira Issue Assistant")

@mcp.tool()
def get_list_projects() -> str:
    """get all the listed Jira projects"""
    data = make_jira_req("GET","/rest/api/3/project")
    return data



