import asyncio

from app.db import SessionLocal
from app.models import Session
from app.services.llm import LLMClient
from app.services.prompts import REVIEW_SYSTEM, build_review_user

async def main():
    db = SessionLocal()
    session = db.query(Session).filter(Session.resume_text != "hello world").first()
    db.close()
    print("Reviewing: ", session.resume_filename)

    client = LLMClient()
    result = await client.chat(REVIEW_SYSTEM, build_review_user(session.resume_text))

    for key in ("strengths", "weaknesses", "story_prompts"):
        print(f"\n{key.upper()}:")
        for item in result.get(key, []):
            print(" -", item)

asyncio.run(main())