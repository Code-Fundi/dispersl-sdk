import asyncio

from dispersl import AsyncDisperslClient


async def main() -> None:
    client = AsyncDisperslClient(
        base_url="https://api.dispersl.com/v1",
        api_key="YOUR_API_KEY",
    )

    created = await client.agents_create(
        {
            "name": "Security Auditor",
            "prompt": "Perform threat-model and compliance-oriented architecture reviews.",
            "description": "Internal security review specialist",
            "category": "security",
            "public": False,
        }
    )

    agent_id = created["data"][0]["id"]
    await client.agents_edit(agent_id, {"description": "Updated by lifecycle example", "active": True})
    fetched = await client.agent_by_id(agent_id)
    print("Fetched agent:", fetched["data"][0]["name_id"])

    listed = await client.agents(limit=20)
    for agent in listed["data"]:
        print(
            {
                "id": agent.get("id"),
                "name_id": agent.get("name_id"),
                "stars_count": agent.get("stars_count", 0),
                "clone_count": agent.get("clone_count", 0),
            }
        )

    await client.agent_delete(agent_id)
    print("Deleted agent", agent_id)
    await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
