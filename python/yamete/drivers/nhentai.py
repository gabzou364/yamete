"""Driver for nhentai.net."""

import re
from typing import Dict
from bs4 import BeautifulSoup
from yamete.driver_interface import DriverInterface


class NHentai(DriverInterface):
    """Driver for nhentai.net."""
    
    DOMAIN = 'nhentai.net'
    
    def __init__(self):
        super().__init__()
        self.matches = {}
    
    def can_handle(self) -> bool:
        """Check if URL is from nhentai.net."""
        if not self.url:
            return False
        
        pattern = rf'^https?://{re.escape(self.DOMAIN)}/g/(\d+)/?'
        match = re.match(pattern, self.url)
        
        if match:
            self.matches['id'] = match.group(1)
            return True
        
        return False
    
    def get_downloadables(self) -> Dict[str, str]:
        """Get all downloadable images from the gallery."""
        session = self.get_session()
        
        try:
            response = session.get(self.url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch page: {e}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get gallery title for folder name
        title_elem = soup.find('h1', class_='title')
        if title_elem:
            title = title_elem.get_text().strip()
            # Clean title for use as folder name
            title = re.sub(r'[<>:"/\\|?*]', '', title)[:100]
        else:
            title = self.matches['id']
        
        folder = f"{self.DOMAIN}/{title}"
        downloadables = {}
        
        # Find all thumbnail images
        thumbs = soup.find_all('a', class_='gallerythumb')
        
        for idx, thumb in enumerate(thumbs):
            img = thumb.find('img')
            if img and 'data-src' in img.attrs:
                thumb_url = img['data-src']
                
                # Convert thumbnail URL to full image URL
                # nhentai thumbnails: i.nhentai.net/galleries/{id}/thumb.jpg
                # Full images: i.nhentai.net/galleries/{id}/1.jpg
                image_url = thumb_url.replace('t.nhentai.net', 'i.nhentai.net')
                image_url = re.sub(r't\.([a-z]+)$', r'.\1', image_url)
                image_url = re.sub(r'/(\d+)t\.', f'/{idx + 1}.', image_url)
                
                # Create filename
                ext = image_url.split('.')[-1]
                filename = f"{folder}/{str(idx + 1).zfill(5)}.{ext}"
                downloadables[filename] = image_url
        
        return downloadables
