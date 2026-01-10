"""Result iterator for downloadable resources."""

from typing import Iterator, Dict
from yamete.downloadable import Downloadable
from yamete.driver_interface import DriverInterface
import os


class ResultIterator:
    """Iterator for downloadable resources."""
    
    def __init__(self, driver: DriverInterface, downloads_dir: str = "downloads"):
        """
        Initialize result iterator.
        
        Args:
            driver: Driver that provides downloadables
            downloads_dir: Base directory for downloads
        """
        self.driver = driver
        self.downloads_dir = downloads_dir
        self.downloadables = driver.get_downloadables()
        self._items = list(self.downloadables.items())
        self._index = 0
    
    def __iter__(self) -> Iterator[Downloadable]:
        """Return iterator."""
        self._index = 0
        return self
    
    def __next__(self) -> Downloadable:
        """Get next downloadable."""
        if self._index >= len(self._items):
            raise StopIteration
        
        path, url = self._items[self._index]
        self._index += 1
        
        # Make path absolute with downloads directory
        if not os.path.isabs(path):
            path = os.path.join(self.downloads_dir, path)
        
        return Downloadable(self.driver.get_session(), path, url)
    
    def __len__(self) -> int:
        """Get number of downloadables."""
        return len(self._items)
    
    def get_items(self) -> Dict[str, str]:
        """Get all items as dict."""
        return self.downloadables
