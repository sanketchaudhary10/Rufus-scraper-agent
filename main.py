import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from rufus_api import RufusAPI


# Loading environment variables from the .env file
load_dotenv()

# Creating the FastAPI application
app = FastAPI(
    title="Rufus Scraper Agent",
    description="AI web scraping agent for structured data extraction",
    version="1.0.0"
)

# Accessing the environment variables
api_key = os.getenv('RUFUS_API_KEY')

# Initializing the Rufus API with the key
client = RufusAPI(api_key=api_key)


# Defining the request body for the scraping endpoint
class ScrapeRequest(BaseModel):
    url: str
    instructions: str
    output_format: str = "json"


# Root endpoint to check if the application is running
@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "Rufus Scraper Agent"
    }


# Health endpoint to check the application status
@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


# Scraping data from the requested URL asynchronously
@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    try:
        result = await client.scrape(
            request.url,
            request.instructions,
            output_format=request.output_format
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    # Checking if the scraper returned a valid result
    if result is None:
        raise HTTPException(
            status_code=500,
            detail="Scraping failed"
        )

    # Returning the scraped data
    return {
        "status": "success",
        "result": result
    }


# Starting the FastAPI server
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
