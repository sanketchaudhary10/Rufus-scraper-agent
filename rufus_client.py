import asyncio
from spacy import load
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from pydantic import BaseModel
from utils.nlp_utils import load_nlp_model
from utils.scraping_utils import parse_html
import os, re, json, csv, random
from urllib.parse import urljoin
from typing import List, Optional
import requests
from playwright_stealth import stealth


class ScrapedDocument(BaseModel):
    url: str
    title: str
    content: List[str]  

class RufusClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("RUFUS_API_KEY")

        if not self.api_key:
            raise ValueError("API key is required. Set RUFUS_API_KEY environment variable or pass it as an argument.")

        self.nlp = load_nlp_model()
        self.rate_limit = 5  # Time to wait between requests to avoid rate-limiting

    def _analyze_prompt(self, instructions):
        
        doc = self.nlp(instructions)
        keywords = [
            token.text for token in doc 
            if token.pos_ in ['NOUN', 'PROPN', 'NUM', 'ADJ', 'DET'] and not token.is_stop and len(token.text) > 2
        ]

        return keywords


    async def scrape(self, url, instructions, output_format):
        try:
            # print("Initializing Playwright...")  

            async with async_playwright() as p:
                # print("Launching browser...")  
                browser = await p.chromium.launch(headless=True)

                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    viewport={"width": random.randint(1000, 1920), "height": random.randint(600, 1080)}
                )

                # print("Opening new page...")
                page = await context.new_page()

                # print("Applying stealth mode manually...")  
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)

                # print(f"Navigating to: {url}")
                await page.goto(url, timeout=10000)
                await page.wait_for_timeout(5000)

                # print("Extracting page content...")
                content = await page.content()
                soup = parse_html(content)

                # print("Analyzing prompt...")
                query = self._analyze_prompt(instructions)
                print(f"Extracting based on query: {query}")

                page_title = await page.title()
                extracted_data = self._process_content(soup, query)

                # print("Following links...")
                nested_data = await self._follow_links(soup, url, query, context)
                extracted_data.extend(nested_data)

                # print("Closing browser...")
                await browser.close()
                print("Scraping completed successfully.")

                return self._synthesize_document(url, page_title, extracted_data, output_format)

        except Exception as e:
            print(f"Error fetching {url}: {e}")  # Full error details
            return None


    def _process_content(self, soup, query):
        """
        Dynamically extracts the content from a webpage based on keywords from the query.
        """
        data = []
        
        # Iterating over common HTML elements
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'span', 'div', 'li', 'table', 'td', 'form', 'input']):
            text = tag.get_text().strip().lower()
            
            # Matching any relevant keyword from the user query to select content
            if any(keyword.lower() in text for keyword in query):
                data.append(tag.get_text().strip())
        
        return data

    async def _follow_links(self, soup, base_url, query, context, max_links=5):
        """
        Follows and scrapes links to nested pages
        """
        nested_data = []
        links = soup.find_all('a', href=True)
        followed_links = 0

        for link in links:
            if followed_links >= max_links:
                break
            
            nested_url = urljoin(base_url, link['href'])

            try:
                await asyncio.sleep(self.rate_limit)

                # Opens a new page
                page = await context.new_page()
                await page.goto(nested_url)
                await page.wait_for_timeout(3000)
                nested_content = await page.content()
                await page.close()

                nested_soup = parse_html(nested_content)
                nested_data.append(f"Link: {nested_url}")
                nested_data.extend(self._process_content(nested_soup, query))
                followed_links += 1

            except Exception as e:
                print(f"Failed to fetch nested page: {nested_url}. Error: {e}")

        return nested_data



    def _synthesize_document(self, url, title, content, output_format="json"):
        """
        Synthesizes the extracted content into a structured document format such as json or CSV based on the user's prompt
        """
        if output_format == "json":
            return self._save_json(ScrapedDocument(url=url, title=title, content=content))
        elif output_format == "csv":
            return self._save_csv(ScrapedDocument(url=url, title=title, content=content))
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _save_json(self, document: ScrapedDocument):
        """
        Saves the synthesized document in JSON format for easy integration into RAG systems.
        """
        output_dir = "extracted_data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        sanitized_url = re.sub(r'https?://', '', document.url)
        sanitized_url = re.sub(r'[^\w\-]', '_', sanitized_url)

        json_filename = f"scraped_data_{sanitized_url}.json"
        json_filepath = os.path.join(output_dir, json_filename)
        
        # Saves the data as JSON
        with open(json_filepath, 'w') as json_file:
            json.dump(document.dict(), json_file, indent=4)
        
        return f"Data saved to {json_filepath}"

    def _save_csv(self, document: ScrapedDocument):
        """
        Saves the synthesized document in CSV format for easy integration into RAG systems.
        """
        output_dir = "extracted_data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generates a sanitized filename from the URL
        sanitized_url = re.sub(r'https?://', '', document.url)
        sanitized_url = re.sub(r'[^\w\-]', '_', sanitized_url)

        csv_filename = f"scraped_data_{sanitized_url}.csv"
        csv_filepath = os.path.join(output_dir, csv_filename)

        # Saves the data as CSV
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["URL", "Title", "Content"])

            for line in document.content:
                writer.writerow([document.url, document.title, line])

        return f"Data saved to {csv_filepath}"
