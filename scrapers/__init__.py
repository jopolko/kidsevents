"""
Toronto Kids Events Data Scrapers Package

This package contains scrapers and utilities for collecting
free kids events in Toronto from various sources.
"""

__version__ = '1.0.0'
__author__ = 'Toronto Kids Events Team'

from .tpl_scraper import TPLScraper
from .eventbrite_fetcher import EventBriteFetcher
from .data_aggregator import DataAggregator

__all__ = [
    'TPLScraper',
    'EventBriteFetcher',
    'DataAggregator'
]
