from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import asyncio

uri = "mongodb+srv://borinesq:5ZZM0k96nB7WjzD6@chesnutmunia.t3jjqqf.mongodb.net/?retryWrites=true&w=majority&appName=ChesnutMunia"
database_names = ["sample_users"]

mongo_databases = {}

# Initialize connections
client = AsyncIOMotorClient(uri, server_api=ServerApi("1"))

for db_name in database_names:
    mongo_databases[db_name] = client[db_name]


def get_mongo_db(database_name: str):
    """
    Returns the MongoDB database object for the given database name.
    """
    if database_name not in mongo_databases:
        raise KeyError(f"MongoDB database '{database_name}' not recognized.")
    return mongo_databases[database_name]


class MongoDatabaseSession:
    def __init__(self, database_name: str):
        if database_name not in mongo_databases:
            raise KeyError(f"MongoDB database '{database_name}' not recognized.")
        self.database_name = database_name

    def __call__(self):
        return mongo_databases[self.database_name]


# Function to send a ping and confirm a successful connection
async def ping_mongo():
    try:
        # Send a ping asynchronously
        await client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(f"Error: {e}")


# Running the async function
asyncio.run(ping_mongo())
