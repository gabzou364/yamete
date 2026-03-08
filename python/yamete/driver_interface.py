"""Base driver interface for site-specific implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import requests


class DriverInterface(ABC):
    """Abstract base class for all site drivers."""
    
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'
    
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
            self.session.headers.update({'User-Agent': self.USER_AGENT})
        if proxies:
            self.session.proxies.update(proxies)
        return self.session
    
    def clean(self) -> 'DriverInterface':
        """Clean up resources."""
        if self.session:
            self.session.close()
            self.session = None
        return self
