"""
backend/app/data/__init__.py - Data Provider Package
"""

from backend.app.data.provider import ResilientProvider, DataResult
from backend.app.data.cached import CachedProvider
from backend.app.data.live import LiveProvider

cached_provider = CachedProvider()
live_provider = LiveProvider()
resilient_provider = ResilientProvider(live_provider=live_provider, cached_provider=cached_provider)

