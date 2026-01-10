"""Downloadable resource class."""

import os
from typing import Optional
import requests


class Downloadable:
    """Represents a downloadable resource."""
    
    def __init__(self, session: requests.Session, path: str, url: str):
        """
        Initialize downloadable resource.
        
        Args:
            session: HTTP session for downloading
            path: Local file path to save to
            url: URL to download from
        """
        self.session = session
        self.path = path
        self.url = url
    
    def get_path(self) -> str:
        """Get the local file path."""
        return self.path
    
    def get_url(self) -> str:
        """Get the download URL."""
        return self.url
    
    def download(self) -> requests.Response:
        """Download the resource to the specified path."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        
        # Download with streaming to handle large files
        response = self.session.get(self.url, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open(self.path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        
        return response
