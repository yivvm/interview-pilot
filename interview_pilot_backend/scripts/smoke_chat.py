import asyncio

from app.services.llm import LLMClient

async def main():
    client = LLMClient()
    reply = await client.chat_messages(
        system="You are a helpful career coach. Reply in 1-2 sentences.",
        messages=[
            {"role": "user","content": "Give me one tip to improve a software engineering resume."}
        ]
    )
    print(type(reply))
    print(reply)


asyncio.run(main())