"""
Basic usage examples for GDELT Article Collector
"""

import requests
from datetime import datetime, timedelta

API_URL = "http://localhost:8004"


def example_1_simple_search():
    """Example 1: Simple keyword search"""
    print("\n=== Example 1: Simple Keyword Search ===")
    
    response = requests.post(f"{API_URL}/search", json={
        "keywords": ["artificial intelligence"],
        "timespan": "7d",
        "max_results": 10
    })
    
    result = response.json()
    print(f"Found {result['count']} articles")
    
    for i, article in enumerate(result['articles'][:5], 1):
        print(f"\n{i}. {article.get('title', 'No title')}")
        print(f"   Source: {article.get('domain', 'Unknown')}")
        print(f"   URL: {article.get('url', 'No URL')}")


def example_2_advanced_filtering():
    """Example 2: Advanced filtering with multiple criteria"""
    print("\n=== Example 2: Advanced Filtering ===")
    
    response = requests.post(f"{API_URL}/search", json={
        "keywords": ["climate change", "renewable energy"],
        "domains": ["bbc.com", "reuters.com", "theguardian.com"],
        "countries": ["US", "GB", "DE"],
        "themes": ["ENV_CLIMATECHANGE"],
        "timespan": "30d",
        "max_results": 20
    })
    
    result = response.json()
    print(f"Found {result['count']} climate articles from trusted sources")
    print(f"Filters: {result['filters']}")


def example_3_korean_news():
    """Example 3: Search Korean news"""
    print("\n=== Example 3: Korean News ===")
    
    response = requests.post(f"{API_URL}/search", json={
        "keywords": ["인공지능", "기술"],
        "countries": ["KR"],
        "languages": ["kor"],
        "timespan": "7d",
        "max_results": 10
    })
    
    result = response.json()
    print(f"Found {result['count']} Korean articles")
    
    for article in result['articles'][:3]:
        print(f"\n- {article.get('title')}")
        print(f"  {article.get('url')}")


def example_4_timeline_analysis():
    """Example 4: Timeline analysis"""
    print("\n=== Example 4: Timeline Analysis ===")
    
    response = requests.post(f"{API_URL}/timeline", json={
        "keywords": ["AI"],
        "timespan": "30d",
        "mode": "TimelineVol"
    })
    
    result = response.json()
    print(f"Timeline with {result['count']} data points")
    
    # Show first few data points
    for point in result['timeline'][:5]:
        print(f"  {point}")


def example_5_domain_specific():
    """Example 5: Domain-specific search"""
    print("\n=== Example 5: Tech News from Specific Sites ===")
    
    tech_domains = [
        "techcrunch.com",
        "theverge.com",
        "arstechnica.com",
        "wired.com"
    ]
    
    response = requests.post(f"{API_URL}/search", json={
        "keywords": ["startup", "funding"],
        "domains": tech_domains,
        "timespan": "7d",
        "max_results": 15
    })
    
    result = response.json()
    print(f"Found {result['count']} startup articles")
    
    # Group by domain
    by_domain = {}
    for article in result['articles']:
        domain = article.get('domain', 'unknown')
        by_domain[domain] = by_domain.get(domain, 0) + 1
    
    print("\nArticles by source:")
    for domain, count in by_domain.items():
        print(f"  {domain}: {count}")


def example_6_export_to_csv():
    """Example 6: Export results to CSV"""
    print("\n=== Example 6: Export to CSV ===")
    
    # First, get articles
    search_response = requests.post(f"{API_URL}/search", json={
        "keywords": ["technology"],
        "timespan": "1d",
        "max_results": 50
    })
    
    articles = search_response.json()['articles']
    
    # Export to CSV
    export_response = requests.post(f"{API_URL}/export", json={
        "articles": articles,
        "filename": "tech_news.csv"
    })
    
    result = export_response.json()
    print(f"Exported {result['count']} articles to {result['filepath']}")
    print(f"Download URL: {result['download_url']}")


def example_7_date_range():
    """Example 7: Specific date range search"""
    print("\n=== Example 7: Specific Date Range ===")
    
    # Get articles from specific month
    response = requests.post(f"{API_URL}/search", json={
        "keywords": ["quantum computing"],
        "start_date": "2024-11-01",
        "end_date": "2024-11-30",
        "max_results": 20
    })
    
    result = response.json()
    print(f"Found {result['count']} quantum computing articles in November")


def example_8_theme_monitoring():
    """Example 8: Theme-based monitoring"""
    print("\n=== Example 8: Economic News ===")
    
    response = requests.post(f"{API_URL}/search", json={
        "themes": ["ECON", "ECON_BANKRUPTCY"],
        "countries": ["US"],
        "timespan": "7d",
        "max_results": 15
    })
    
    result = response.json()
    print(f"Found {result['count']} economic articles")


def example_9_get_available_filters():
    """Example 9: Get available themes and countries"""
    print("\n=== Example 9: Available Filters ===")
    
    # Get themes
    themes_response = requests.get(f"{API_URL}/themes")
    themes = themes_response.json()
    print(f"\nAvailable themes: {len(themes['themes'])}")
    print(themes['themes'][:5], "...")
    
    # Get countries
    countries_response = requests.get(f"{API_URL}/countries")
    countries = countries_response.json()
    print(f"\nCommon countries: {countries['countries']}")


def main():
    """Run all examples"""
    print("GDELT Article Collector - Usage Examples")
    print("=" * 50)
    
    try:
        # Check if service is running
        health = requests.get(f"{API_URL}/health")
        if health.status_code == 200:
            print("✓ Service is running")
        else:
            print("✗ Service not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to service. Make sure it's running:")
        print("  docker-compose up -d")
        print("  or")
        print("  python main.py")
        return
    
    # Run examples
    examples = [
        example_1_simple_search,
        example_2_advanced_filtering,
        example_3_korean_news,
        example_4_timeline_analysis,
        example_5_domain_specific,
        example_6_export_to_csv,
        example_7_date_range,
        example_8_theme_monitoring,
        example_9_get_available_filters
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
        
        print("\n" + "-" * 50)


if __name__ == "__main__":
    main()
