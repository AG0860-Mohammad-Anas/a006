import asyncio

from src.host import run_agent


async def main():
    print("=" * 60)
    print("A006 MCP Host for Jira Issue Assistant")
    print("=" * 60)
    print("Type 'exit' to quit.\n")

    while True:
        try:
            query = input("Enter your Jira query: ").strip()
        except EOFError:
            print("\nGoodbye!")
            break

        if query.lower() in ["exit", "quit"]:
            print("\nGoodbye!")
            break

        if not query:
            print("Please enter a query.\n")
            continue

        await run_agent(query)


if __name__ == "__main__":
    asyncio.run(main())