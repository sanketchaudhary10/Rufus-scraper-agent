from rufus_client import RufusClient
from rufus_api import RufusAPI
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables from the .env file
load_dotenv()

# Access the environment variables
api_key = os.getenv('RUFUS_API_KEY')

# Initialize the Rufus API with the key
client = RufusAPI(api_key=api_key)

# Instructions for scraping
instructions = "Find all the five star reviews for Apple iphone15 on Amazon"

# Scrape data from the URL asynchronously
async def main():
    documents = await client.scrape("https://www.amazon.com/s?k=iphone+15&crid=14V1QK01HSLTS&sprefix=iphone+15%2Caps%2C144&ref=nb_sb_noss_1", instructions, output_format="csv")
    print(documents)


if __name__ == "__main__":
    asyncio.run(main())