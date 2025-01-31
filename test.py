import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_connection():
    # Retrieve MongoDB URI from environment variable with fallback for testing
    uri = os.getenv(
        "MONGODB_URI",
        "mongodb+srv://Atul1603:Atuldubey@pdftoaudio.8pkov.mongodb.net/UserDataBase?retryWrites=true&w=majority&appName=PdfToAudio"
    )
    
    client = None
    try:
        # Create MongoDB client and test connection
        client = AsyncIOMotorClient(uri)
        db = client.UserDataBase
        
        # Perform a simple database operation
        collections = await db.list_collection_names()
        print(f"Collections in the database: {collections}")
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
    finally:
        # Ensure proper cleanup of resources
        if client:
            await client.close()

if __name__ == "__main__":
    # Modern asyncio execution
    asyncio.run(test_connection())