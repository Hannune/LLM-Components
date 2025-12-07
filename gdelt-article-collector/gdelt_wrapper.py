"""
GDELT Article Collector Wrapper
Provides filtering and search capabilities for GDELT database using gdeltdoc
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from gdeltdoc import GdeltDoc, Filters


class GDELTCollector:
    """Wrapper for GDELT article collection with advanced filtering"""
    
    def __init__(self):
        self.gd = GdeltDoc()
        
    def search_articles(
        self,
        keywords: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        countries: Optional[List[str]] = None,
        themes: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        max_results: int = 250,
        timespan: Optional[str] = None,
        sort_by: str = "date"
    ) -> Dict[str, Any]:
        """
        Search GDELT articles with multiple filters

        Args:
            keywords: List of keywords to search for (e.g., ["AI", "machine learning"])
            domains: List of domains to filter (e.g., ["bbc.com", "cnn.com"])
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            countries: List of country codes (e.g., ["US", "GB", "KR"])
            themes: List of GDELT themes (e.g., ["ECON", "ENV_CLIMATECHANGE"])
            languages: List of language codes (e.g., ["eng", "kor"])
            max_results: Maximum number of results (default: 250)
            timespan: Quick timespan option ("24h", "1d", "7d", "30d") - overrides dates
            sort_by: Sort field ("date", "relevance")

        Returns:
            Dict with articles (DataFrame), metadata, and stats
        """
        # Build filter object with keyword parameter
        filter_kwargs = {}

        # Handle keywords - join multiple keywords
        if keywords:
            keyword_query = " OR ".join(keywords)
            filter_kwargs['keyword'] = keyword_query

        # Handle timespan using the API's built-in timespan parameter
        if timespan:
            filter_kwargs['timespan'] = timespan
        else:
            # Use date range if no timespan
            if start_date:
                filter_kwargs['start_date'] = start_date
            if end_date:
                filter_kwargs['end_date'] = end_date

        # Add other filters
        if domains:
            filter_kwargs['domain'] = domains
        if countries:
            filter_kwargs['country'] = countries
        if themes:
            filter_kwargs['theme'] = themes
        if languages:
            filter_kwargs['language'] = languages

        # Create Filters object with parameters
        f = Filters(**filter_kwargs)

        # Execute search
        try:
            articles_df = self.gd.article_search(f)

            if articles_df.empty:
                return {
                    "success": True,
                    "articles": [],
                    "count": 0,
                    "filters": self._get_filter_summary(f, timespan),
                    "message": "No articles found with given filters"
                }

            # Sort results
            if sort_by == "date" and "seendate" in articles_df.columns:
                articles_df = articles_df.sort_values("seendate", ascending=False)

            # Limit results
            if max_results and len(articles_df) > max_results:
                articles_df = articles_df.head(max_results)

            # Convert to list of dicts
            articles = articles_df.to_dict("records")

            return {
                "success": True,
                "articles": articles,
                "count": len(articles),
                "filters": self._get_filter_summary(f, timespan),
                "columns": list(articles_df.columns)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "articles": [],
                "count": 0,
                "filters": self._get_filter_summary(f, timespan)
            }
    
    def get_timeline(
        self,
        keywords: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timespan: Optional[str] = None,
        mode: str = "ArtList"
    ) -> Dict[str, Any]:
        """
        Get timeline of article counts over time

        Args:
            mode: "ArtList" (article list) or "TimelineVol" (volume over time)
            Other args same as search_articles

        Returns:
            Dict with timeline data
        """
        filter_kwargs = {}

        # Handle keywords
        if keywords:
            keyword_query = " OR ".join(keywords)
            filter_kwargs['keyword'] = keyword_query

        # Handle timespan using the API's built-in timespan parameter
        if timespan:
            filter_kwargs['timespan'] = timespan
        else:
            # Use date range if no timespan
            if start_date:
                filter_kwargs['start_date'] = start_date
            if end_date:
                filter_kwargs['end_date'] = end_date

        # Add other filters
        if domains:
            filter_kwargs['domain'] = domains

        # Create Filters object with parameters
        f = Filters(**filter_kwargs)

        try:
            timeline_df = self.gd.timeline_search(mode, f)

            if timeline_df.empty:
                return {
                    "success": True,
                    "timeline": [],
                    "count": 0,
                    "mode": mode
                }

            timeline = timeline_df.to_dict("records")

            return {
                "success": True,
                "timeline": timeline,
                "count": len(timeline),
                "mode": mode,
                "filters": self._get_filter_summary(f, timespan)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timeline": [],
                "count": 0
            }
    
    def export_to_csv(self, articles: List[Dict], filepath: str) -> Dict[str, Any]:
        """Export articles to CSV file"""
        try:
            df = pd.DataFrame(articles)
            df.to_csv(filepath, index=False)
            return {
                "success": True,
                "filepath": filepath,
                "count": len(articles)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_filter_summary(self, filters: Filters, timespan: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of applied filters"""
        summary = {}
        
        if hasattr(filters, 'keyword') and filters.keyword:
            summary['keywords'] = filters.keyword
        if hasattr(filters, 'domain') and filters.domain:
            summary['domains'] = filters.domain
        if hasattr(filters, 'start_date') and filters.start_date:
            summary['start_date'] = filters.start_date
        if hasattr(filters, 'end_date') and filters.end_date:
            summary['end_date'] = filters.end_date
        if hasattr(filters, 'country') and filters.country:
            summary['countries'] = filters.country
        if hasattr(filters, 'theme') and filters.theme:
            summary['themes'] = filters.theme
        if hasattr(filters, 'language') and filters.language:
            summary['languages'] = filters.language
        if timespan:
            summary['timespan'] = timespan
            
        return summary
    
    @staticmethod
    def get_available_themes() -> List[str]:
        """Get list of common GDELT themes"""
        return [
            "ECON",
            "ECON_BANKRUPTCY",
            "ENV_CLIMATECHANGE",
            "HEALTH",
            "TERROR",
            "WB_2737_TECHNOLOGY_AND_INNOVATION",
            "LEADER",
            "MILITARY",
            "CRISIS",
            "SCANDAL",
            "DIPLOMACY"
        ]
    
    @staticmethod
    def get_available_countries() -> List[str]:
        """Get list of common country codes"""
        return [
            "US",  # United States
            "GB",  # United Kingdom
            "CN",  # China
            "KR",  # South Korea
            "JP",  # Japan
            "DE",  # Germany
            "FR",  # France
            "IN",  # India
            "RU",  # Russia
            "BR",  # Brazil
        ]
