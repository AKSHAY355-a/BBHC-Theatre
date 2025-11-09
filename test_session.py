"""Test if Telegram session is valid"""
import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH

async def test_session():
    # Try admin session
    client = TelegramClient('admin_919353589504', int(API_ID), API_HASH)
    await client.connect()
    
    if await client.is_user_authorized():
        print("✅ Admin session is VALID and authorized!")
        me = await client.get_me()
        print(f"   Logged in as: {me.first_name} {me.last_name or ''}")
        print(f"   Phone: {me.phone}")
    else:
        print("❌ Admin session is NOT authorized")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_session())
