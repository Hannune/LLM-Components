"""
Example: Using the GDELT Collector via REST API
Demonstrates how to call the FastAPI endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8004"

def search_articles():
    """Example: Search for articles"""
    print("Example 1: Search for AI articles in the last 7 days")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/search",
        json={
            "keywords": ["artificial intelligence", "machine learning"],
            "timespan": "7d",
            "max_results": 5,
            "domains": ["bbc.com", "cnn.com", "reuters.com"]
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"Success: Found {data['count']} articles\n")

        for i, article in enumerate(data['articles'][:3], 1):
            print(f"{i}. {article['title']}")
            print(f"   URL: {article['url']}")
            print(f"   Domain: {article['domain']}")
            print(f"   Date: {article['seendate']}\n")
    else:
        print(f"Error: {response.status_code}")

def search_by_country():
    """Example: Search by country"""
    print("\nExample 2: Search for tech news from specific countries")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/search",
        json={
            "keywords": ["technology"],
            "timespan": "24h",
            "countries": ["US", "GB", "KR"],
            "max_results": 5
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"Success: Found {data['count']} articles from US, GB, KR\n")

        for article in data['articles'][:3]:
            print(f"- {article['title']}")
            print(f"  Country: {article.get('sourcecountry', 'N/A')}")
            print(f"  Language: {article.get('language', 'N/A')}\n")

def get_available_filters():
    """Example: Get available themes and countries"""
    print("\nExample 3: Get available filters")
    print("=" * 60)

    # Get themes
    themes_response = requests.get(f"{BASE_URL}/themes")
    if themes_response.status_code == 200:
        themes = themes_response.json()
        print(f"Available themes: {', '.join(themes['themes'][:5])}...\n")

    # Get countries
    countries_response = requests.get(f"{BASE_URL}/countries")
    if countries_response.status_code == 200:
        countries = countries_response.json()
        print(f"Available countries: {', '.join(countries['countries'])}\n")

def main():
    """Run all examples"""
    print("GDELT Article Collector - API Usage Examples")
    print("=" * 60)
    print()

    try:
        search_articles()
        search_by_country()
        get_available_filters()
        print("\nAll examples completed successfully!")
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to GDELT API service.")
        print("Make sure the service is running: docker compose up -d")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
