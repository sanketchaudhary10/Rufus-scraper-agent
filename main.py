from rufus_client import RufusClient
from rufus_api import RufusAPI
import os
from dotenv import load_dotenv
import asyncio

# Loading environment variables from the .env file
load_dotenv()

# Accessing the environment variables
api_key = os.getenv('RUFUS_API_KEY')

# Initializing the Rufus API with the key
client = RufusAPI(api_key=api_key)

# Instructions/Prompts for scraping
instructions = "Find all the information about Graduate Admissions page"

# Scraping data from the URL asynchronously
async def main():
    documents = await client.scrape("https://ucsd.edu/admissions-aid/", instructions, output_format="json")
    print(documents)


if __name__ == "__main__":
    asyncio.run(main())