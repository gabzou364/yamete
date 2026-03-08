"""Base driver interface for site-specific implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import requests


class DriverInterface(ABC):
    """Abstract base class for all site drivers."""
    
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    
    DEFAULT_HEADERS = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
    
    def __init__(self):
        self.url: Optional[str] = None
        self.session: Optional[requests.Session] = None
    
    def set_url(self, url: str) -> 'DriverInterface':
        """Set the URL to be processed."""
        self.url = url
        return self
    
    @abstractmethod
    def can_handle(self) -> bool:
        """Check if this driver can handle the set URL."""
        pass
    
    @abstractmethod
    def get_downloadables(self) -> Dict[str, str]:
        """
        Get downloadable URLs.
        
        Returns:
            Dict mapping file paths to download URLs
        """
        pass
    
    def get_session(self, proxies: Optional[Dict[str, str]] = None) -> requests.Session:
        """Get or create HTTP session with proxy support."""
        if self.session is None:
            self.session = requests.Session()
            self.session.headers.update(self.DEFAULT_HEADERS)
        if proxies:
            self.session.proxies.update(proxies)
        return self.session
    
    def clean(self) -> 'DriverInterface':
        """Clean up resources."""
        if self.session:
            self.session.close()
            self.session = None
        return self
