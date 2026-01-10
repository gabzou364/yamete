"""
Example custom driver for Yamete Python CLI

This demonstrates how to create a custom driver for a new site.
Copy this file to python/yamete/drivers/ and modify it for your site.
"""

import re
from typing import Dict
from bs4 import BeautifulSoup
from yamete.driver_interface import DriverInterface


class ExampleSite(DriverInterface):
    """
    Example driver for example-site.com.
    
    Replace this with your site's domain and logic.
    """
    
    DOMAIN = 'example-site.com'  # Change to your site's domain
    
    def __init__(self):
        super().__init__()
        self.matches = {}
    
    def can_handle(self) -> bool:
        """
        Check if this driver can handle the URL.
        
        Returns:
            True if the URL matches this site's pattern, False otherwise
        """
        if not self.url:
            return False
        
        # Example pattern: https://example-site.com/gallery/12345
        # Modify this regex to match your site's URL structure
        pattern = rf'^https?://{re.escape(self.DOMAIN)}/gallery/(?P<gallery_id>\d+)/?$'
        match = re.match(pattern, self.url)
        
        if match:
            # Store captured groups for use in get_downloadables
            self.matches = match.groupdict()
            return True
        
        return False
    
    def get_downloadables(self) -> Dict[str, str]:
        """
        Extract all downloadable URLs from the page.
        
        Returns:
            Dictionary mapping local file paths to download URLs
            Example: {'example-site.com/gallery-123/00001.jpg': 'https://cdn.example.com/img1.jpg'}
        """
        session = self.get_session()
        
        # Fetch the gallery page
        try:
            response = session.get(self.url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch page: {e}")
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract gallery title (optional, for better folder names)
        title_elem = soup.find('h1', class_='gallery-title')  # Adjust selector for your site
        if title_elem:
            title = title_elem.get_text().strip()
            # Clean title for use as folder name
            title = re.sub(r'[<>:"/\\|?*]', '', title)[:100]
        else:
            title = self.matches['gallery_id']
        
        # Create folder path
        folder = f"{self.DOMAIN}/{title}"
        
        downloadables = {}
        
        # Find all images in the gallery
        # Adjust these selectors to match your site's HTML structure
        images = soup.find_all('img', class_='gallery-image')
        
        for idx, img in enumerate(images):
            # Get image URL from src or data-src attribute
            image_url = img.get('data-src') or img.get('src')
            
            if image_url:
                # Convert relative URLs to absolute
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url.startswith('/'):
                    image_url = f'https://{self.DOMAIN}{image_url}'
                
                # Determine file extension
                ext = image_url.split('.')[-1].split('?')[0]
                if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    ext = 'jpg'  # Default extension
                
                # Create filename with zero-padded index
                filename = f"{folder}/{str(idx + 1).zfill(5)}.{ext}"
                downloadables[filename] = image_url
        
        if not downloadables:
            raise RuntimeError(f"No images found on {self.url}")
        
        return downloadables


# Alternative example: Site with paginated galleries
class ExamplePaginatedSite(DriverInterface):
    """
    Example driver for a site with paginated galleries.
    
    Some sites show thumbnails on the main page, and you need to
    visit each thumbnail page to get the full image URL.
    """
    
    DOMAIN = 'paginated-site.com'
    
    def __init__(self):
        super().__init__()
        self.matches = {}
    
    def can_handle(self) -> bool:
        """Check if URL matches this site."""
        if not self.url:
            return False
        
        pattern = rf'^https?://{re.escape(self.DOMAIN)}/album/(?P<album_id>[^/]+)/?$'
        match = re.match(pattern, self.url)
        
        if match:
            self.matches = match.groupdict()
            return True
        
        return False
    
    def get_downloadables(self) -> Dict[str, str]:
        """Extract images by visiting each page in the gallery."""
        session = self.get_session()
        
        try:
            response = session.get(self.url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch page: {e}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get all page URLs
        page_links = []
        for link in soup.find_all('a', class_='page-link'):  # Adjust selector
            page_url = link.get('href')
            if page_url:
                # Convert to absolute URL if needed
                if page_url.startswith('/'):
                    page_url = f'https://{self.DOMAIN}{page_url}'
                page_links.append(page_url)
        
        folder = f"{self.DOMAIN}/{self.matches['album_id']}"
        downloadables = {}
        
        # Visit each page to get the full image
        for idx, page_url in enumerate(page_links):
            try:
                page_response = session.get(page_url, timeout=30)
                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                
                # Find the main image on the page
                img = page_soup.find('img', id='main-image')  # Adjust selector
                if img and img.get('src'):
                    image_url = img['src']
                    
                    # Convert to absolute URL
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url
                    elif image_url.startswith('/'):
                        image_url = f'https://{self.DOMAIN}{image_url}'
                    
                    ext = image_url.split('.')[-1].split('?')[0]
                    filename = f"{folder}/{str(idx + 1).zfill(5)}.{ext}"
                    downloadables[filename] = image_url
                    
            except Exception as e:
                print(f"Warning: Failed to get image from {page_url}: {e}")
                continue
        
        return downloadables


# Tips for creating drivers:
# 1. Use browser DevTools to inspect the site's HTML structure
# 2. Look for patterns in image URLs
# 3. Check if images are loaded via JavaScript (may need special handling)
# 4. Handle both relative and absolute URLs
# 5. Add error handling for missing elements
# 6. Test with multiple galleries to ensure it works consistently
# 7. Consider pagination, lazy loading, and other dynamic content loading
