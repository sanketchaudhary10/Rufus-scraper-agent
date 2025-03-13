from setuptools import setup, find_packages

setup(
    name="rufus-web-scraper",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "playwright",
        "playwright-stealth",
        "beautifulsoup4",
        "spacy",
        "pydantic",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "rufus=rufus_client:main"
        ]
    },
)