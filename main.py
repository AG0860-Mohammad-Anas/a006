import asyncio
import sys
from src.host import run_agent

def main():
    print("🚀 Starting A006 MCP Host for Jira Issue Assistant...")
    
    # Allow the user to pass a query via the terminal, or use a default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "List all Jira projects"
        
    asyncio.run(run_agent(query))

if __name__ == "__main__":
    main()