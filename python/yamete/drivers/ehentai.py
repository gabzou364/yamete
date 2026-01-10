"""Driver for e-hentai.org."""

import re
from typing import Dict
from bs4 import BeautifulSoup
from yamete.driver_interface import DriverInterface


class EHentai(DriverInterface):
    """Driver for e-hentai.org and exhentai.org."""
    
    DOMAINS = ['e-hentai.org', 'exhentai.org']
    
    def __init__(self):
        super().__init__()
        self.matches = {}
    
    def can_handle(self) -> bool:
        """Check if URL is from e-hentai.org or exhentai.org."""
        if not self.url:
            return False
        
        for domain in self.DOMAINS:
            pattern = rf'^https?://{re.escape(domain)}/g/(\d+)/([a-f0-9]+)/?'
            match = re.match(pattern, self.url)
            
            if match:
                self.matches['gallery_id'] = match.group(1)
                self.matches['gallery_token'] = match.group(2)
                self.matches['domain'] = domain
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
        
        # Get gallery title
        title_elem = soup.find('h1', id='gn')
        if title_elem:
            title = title_elem.get_text().strip()
            # Clean title for use as folder name
            title = re.sub(r'[<>:"/\\|?*]', '', title)[:100]
        else:
            title = self.matches['gallery_id']
        
        folder = f"{self.matches['domain']}/{title}"
        downloadables = {}
        
        # Get all page links
        page_links = []
        gdtm_div = soup.find('div', id='gdt')
        if gdtm_div:
            for link in gdtm_div.find_all('a'):
                if link.get('href'):
                    page_links.append(link['href'])
        
        # Visit each page to get the actual image URL
        for idx, page_url in enumerate(page_links):
            try:
                page_response = session.get(page_url, timeout=30)
                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                
                # Find the main image
                img = page_soup.find('img', id='img')
                if img and img.get('src'):
                    image_url = img['src']
                    ext = image_url.split('.')[-1].split('?')[0]
                    filename = f"{folder}/{str(idx + 1).zfill(5)}.{ext}"
                    downloadables[filename] = image_url
            except Exception as e:
                print(f"Warning: Failed to get image from {page_url}: {e}")
                continue
        
        return downloadables
