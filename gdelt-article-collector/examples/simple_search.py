"""
Simple Example: Search GDELT for Latest Finance Articles
Based on the working gdeltdoc pattern
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gdelt_wrapper import GDELTCollector

def main():
    """Search for latest finance articles"""
    print("GDELT Article Collector - Simple Search Example")
    print("=" * 60)

    # Initialize the collector
    collector = GDELTCollector()

    # Search for finance articles in the last 24 hours (get top 3)
    result = collector.search_articles(
        keywords=["finance"],
        timespan="24h",
        max_results=3
    )

    # Display results
    if result["success"]:
        print(f"\nFound {result['count']} articles:")
        print(f"Filters applied: {result['filters']}\n")

        for i, article in enumerate(result["articles"], 1):
            print(f"{i}. Title: {article.get('title', 'N/A')}")
            print(f"   URL: {article.get('url', 'N/A')}")
            print(f"   Date: {article.get('seendate', 'N/A')}")
            print(f"   Domain: {article.get('domain', 'N/A')}")
            print(f"   Language: {article.get('language', 'N/A')}")
            print("-" * 60)
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        print(f"Message: {result.get('message', 'No message')}")

if __name__ == "__main__":
    main()
