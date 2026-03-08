"""Driver for hdporncomics.com."""

import re
from typing import Dict
from bs4 import BeautifulSoup
from yamete.driver_interface import DriverInterface


class HDPornComics(DriverInterface):
    """Driver for hdporncomics.com."""
    
    DOMAIN = 'hdporncomics.com'
    
    def __init__(self):
        super().__init__()
        self.matches = {}
    
    def can_handle(self) -> bool:
        """Check if URL is from hdporncomics.com."""
        if not self.url:
            return False
        
        # Pattern matches: http(s)://hdporncomics.com/{album}/
        pattern = rf'^https?://{re.escape(self.DOMAIN)}/(?P<album>[^/]+)/$'
        match = re.match(pattern, self.url)
        
        if match:
            self.matches = match.groupdict()
            return True
        
        return False
    
    def get_downloadables(self) -> Dict[str, str]:
        """Get all downloadable images from the album."""
        session = self.get_session()
        session.headers.update({'Referer': f'https://{self.DOMAIN}/'})
        
        try:
            response = session.get(self.url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch page: {e}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        folder = f"{self.DOMAIN}/{self.matches['album']}"
        downloadables = {}
        
        # Find all figure links in the gallery
        # Looking for: .my-gallery figure a
        gallery = soup.find(class_='my-gallery')
        if not gallery:
            # Try alternative selectors
            gallery = soup
        
        figures = gallery.find_all('figure')
        index = 0
        
        for figure in figures:
            link = figure.find('a')
            if link and link.get('href'):
                image_url = link['href']
                
                # Create filename with padding
                basename = image_url.split('/')[-1]
                filename = f"{folder}/{str(index).zfill(5)}-{basename}"
                downloadables[filename] = image_url
                index += 1
        
        # If no figures found, try direct img tags in gallery
        if not downloadables:
            imgs = gallery.find_all('img')
            for img in imgs:
                if img.get('src') and not img['src'].startswith('data:'):
                    image_url = img['src']
                    basename = image_url.split('/')[-1]
                    filename = f"{folder}/{str(index).zfill(5)}-{basename}"
                    downloadables[filename] = image_url
                    index += 1
        
        return downloadables
