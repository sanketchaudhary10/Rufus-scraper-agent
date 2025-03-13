import pytest
from rufus_client import RufusClient


def test_empty_scrape():
    client = RufusClient()
    
    url = "https://chromeenterprise.google/"
    instructions = "Extract pricing details"  
    
    result = client.scrape(url, instructions)
    
    # Asserts that result is not None
    assert result is not None, "Scrape result should not be None"
    
    # Asserts that the "data" field is empty (if the page doesn't have pricing details)
    assert len(result['data']) == 0, "Data field should be empty if no matching content is found"


def test_invalid_url():
    client = RufusClient()
    
    # Provides an invalid or unreachable URL
    url = "https://chromeenterpris.google/"
    instructions = "Find contact information."
    
    result = client.scrape(url, instructions)
    
    # Asserts that the result is None due to invalid URL
    assert result is None, "Scrape result should be None for an invalid URL"

# Tests Function to Run Rufus with Different Prompts
def test_rufus_scraping():
    client = RufusClient()
    
    # Test Case 1: Extract FAQs
    url = "https://chromeenterprise.google/resources/faq/"
    instructions = "Extract FAQs from the page"
    print("Testing FAQ Extraction")
    result_faq = client.scrape(url, instructions, output_format="json")
    print(result_faq)
    
    # Test Case 2: Extract Pricing Details
    url = "https://www.amazon.com/s?k=microwave"
    instructions = "Find pricing details for microwaves"
    print("Testing Pricing Extraction")
    result_pricing = client.scrape(url, instructions, output_format="json")
    print(result_pricing)
    
    # Test Case 3: Extract Application Form Data
    url = "https://jobs.apple.com/en-us/search?location=united-states-USA&team=natural-language-processing-and-speech-technologies-MLAI-NLP"
    instructions = "Extract content from application forms"
    print("Testing Application Form Extraction")
    result_application = client.scrape(url, instructions, output_format="json")
    print(result_application)

# Run the tests
test_rufus_scraping()
