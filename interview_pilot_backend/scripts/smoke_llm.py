import asyncio

from app.services.llm import LLMClient

async def main():
    client = LLMClient()
    out = await client.chat(
        system="You are a helpful assistant that replies only in JSON.",
        user='Return a JSON object with keys "greeting" and "language" '
            "for a friendly hello in French.",
    )
    print(type(out), out)

asyncio.run(main())