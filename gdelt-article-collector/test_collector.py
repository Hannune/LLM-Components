"""
Simple test script for GDELT Article Collector
Based on the working example provided
"""

from gdelt_wrapper import GDELTCollector

def test_basic_search():
    """Test basic article search with finance keyword"""
    print("Testing GDELT Article Collector...")
    print("=" * 50)

    # Initialize collector
    collector = GDELTCollector()

    # Search for finance articles in the last 24 hours (limit to 3)
    result = collector.search_articles(
        keywords=["finance"],
        timespan="24h",
        max_results=3
    )

    if result["success"]:
        print(f"\nFound {result['count']} articles:")
        print(f"Filters applied: {result['filters']}\n")

        for i, article in enumerate(result["articles"], 1):
            print(f"{i}. Title: {article.get('title', 'N/A')}")
            print(f"   URL: {article.get('url', 'N/A')}")
            print(f"   Date: {article.get('seendate', 'N/A')}")
            print("-" * 50)
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        print(f"Message: {result.get('message', 'No message')}")

if __name__ == "__main__":
    test_basic_search()
