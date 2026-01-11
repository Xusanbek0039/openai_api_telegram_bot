import asyncio
import database
import os

async def test_db():
    print("Initializing DB...")
    await database.init_db()
    
    print("Adding user...")
    await database.add_user(12345, "testuser")
    
    print("Fetching user...")
    user = await database.get_user(12345)
    print(f"User found: {user}")
    assert user[1] == "testuser"
    assert user[2] == 0 # Default not premium
    
    print("Upgrading user...")
    await database.set_premium(12345, True)
    
    print("Fetching updated user...")
    user = await database.get_user(12345)
    print(f"User found: {user}")
    assert user[2] == 1 # Is premium
    
    print("Database test passed!")

if __name__ == "__main__":
    if os.path.exists("bot_users.db"):
        os.remove("bot_users.db")
    asyncio.run(test_db())
