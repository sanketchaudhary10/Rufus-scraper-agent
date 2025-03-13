from rufus_client import RufusClient
import os

class RufusAPI:
    def __init__(self, api_key=None):
        """
        Initializes RufusAPI with an optional API key for authentication.
        If no API key is passed, it will attempt to load it from the environment.
        """
        self.api_key = api_key or os.getenv('RUFUS_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required for RufusAPI. Set it as an environment variable or pass it during initialization.")
        self.client = RufusClient()

    async def scrape(self, url, instructions, output_format="json"):
        return await self.client.scrape(url, instructions, output_format=output_format)