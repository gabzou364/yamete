# Yamete Python CLI

Python version of Yamete - A manga/hentai downloader with minimal dependencies.

## Features

- ✅ **Minimal Dependencies**: Only requires `requests`, `beautifulsoup4`, `Pillow`, and `reportlab`
- ✅ **Easy to Use**: Simple command-line interface
- ✅ **Proxy Support**: Built-in proxy support for downloads and dependency fetching
- ✅ **Multiple Input Methods**: Single URL, file list, or interactive mode
- ✅ **PDF Conversion**: Convert downloaded images to PDF
- ✅ **ZIP Archives**: Create ZIP files from downloads
- ✅ **Custom Drivers**: Support for custom site drivers
- ✅ **Error Logging**: Track failed downloads

## Installation

### Quick Start (No Installation)

1. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

2. Run directly:
```bash
python3 yamete.py -u "https://hdporncomics.com/example/"
```

### Install as Package

```bash
pip3 install .
```

Then use the `yamete` command:
```bash
yamete -u "https://hdporncomics.com/example/"
```

## Usage

### Basic Examples

Download a single URL:
```bash
python3 yamete.py -u "https://hdporncomics.com/example/"
```

Download multiple URLs from a file:
```bash
python3 yamete.py -l urls.txt
```

Interactive mode:
```bash
python3 yamete.py -i
```

### Advanced Options

Create a PDF instead of separate images:
```bash
python3 yamete.py -u "https://hdporncomics.com/example/" -p
```

Create a ZIP archive:
```bash
python3 yamete.py -u "https://hdporncomics.com/example/" -z
```

Use a proxy:
```bash
python3 yamete.py -u "https://hdporncomics.com/example/" --proxy http://proxy:8080
```

Save failed URLs to a file:
```bash
python3 yamete.py -l urls.txt -e errors.txt
```

Use custom drivers:
```bash
python3 yamete.py -u "https://example.com/gallery/" -d /path/to/custom/drivers
```

Verbose output:
```bash
python3 yamete.py -u "https://hdporncomics.com/example/" -v
```

### All Options

```
usage: yamete.py [-h] (-u URL | -l LIST | -i) [-p] [-z] [-e ERRORS] 
                 [-d DRIVERS] [--proxy PROXY] [--downloads-dir DOWNLOADS_DIR]
                 [-v] [-q] [--version]

Options:
  -h, --help            Show help message
  -u URL, --url URL     URL to download from
  -l LIST, --list LIST  File with list of URLs (one per line)
  -i, --interactive     Interactive mode (read URLs from stdin)
  -p, --pdf             Create a PDF file instead of separate images
  -z, --zip             Create a ZIP archive
  -e ERRORS, --errors ERRORS
                        File to write failed URLs
  -d DRIVERS, --drivers DRIVERS
                        Directory with custom drivers (can be specified multiple times)
  --proxy PROXY         Proxy URL (e.g., http://proxy:8080 or socks5://proxy:1080)
  --downloads-dir DOWNLOADS_DIR
                        Directory for downloads (default: downloads)
  -v, --verbose         Verbose output
  -q, --quiet           Quiet mode (minimal output)
  --version             Show version
```

## Supported Sites

The Python version currently includes drivers for:

- **hdporncomics.com** (Primary driver)
- nhentai.net
- e-hentai.org / exhentai.org

More drivers can be added easily by following the driver pattern. The PHP version supports 350+ sites, and these can be ported as needed.

## Creating Custom Drivers

Create a new Python file in `python/yamete/drivers/`:

```python
from yamete.driver_interface import DriverInterface
import re
from bs4 import BeautifulSoup

class MySite(DriverInterface):
    DOMAIN = 'mysite.com'
    
    def can_handle(self) -> bool:
        """Check if this driver can handle the URL."""
        pattern = rf'^https?://{re.escape(self.DOMAIN)}/gallery/(\d+)'
        return bool(re.match(pattern, self.url))
    
    def get_downloadables(self) -> dict:
        """Return dict of {filepath: download_url}."""
        session = self.get_session()
        response = session.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        downloadables = {}
        for idx, img in enumerate(soup.find_all('img', class_='gallery-image')):
            url = img['src']
            filename = f"{self.DOMAIN}/gallery/{idx:05d}.jpg"
            downloadables[filename] = url
        
        return downloadables
```

## Proxy Support

Yamete Python CLI supports HTTP and SOCKS proxies for both downloading content and fetching dependencies:

### Using Proxy for Downloads

```bash
# HTTP proxy
python3 yamete.py -u "https://example.com/gallery/" --proxy http://proxy.example.com:8080

# SOCKS5 proxy (requires PySocks: pip install PySocks)
python3 yamete.py -u "https://example.com/gallery/" --proxy socks5://proxy.example.com:1080
```

### Using Proxy for Installing Dependencies

```bash
# Set proxy for pip
pip3 install --proxy http://proxy.example.com:8080 -r requirements.txt

# Or use environment variables
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
pip3 install -r requirements.txt
```

## Comparison with PHP Version

| Feature | PHP Version | Python Version |
|---------|-------------|----------------|
| Dependencies | Many (Guzzle, Symfony, etc.) | Minimal (4 packages) |
| Sites Supported | 350+ | 3 (easily expandable) |
| Proxy Support | ❌ | ✅ |
| PDF Creation | ✅ | ✅ |
| ZIP Archives | ✅ | ✅ |
| Custom Drivers | ✅ | ✅ |
| Installation | Composer required | pip or standalone |
| Easy to Use | Medium | High |

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

Dependencies:
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `Pillow` - Image processing
- `reportlab` - PDF generation

## Troubleshooting

### ImportError or Module Not Found

Make sure dependencies are installed:
```bash
pip3 install -r requirements.txt
```

### Proxy Not Working

For SOCKS proxies, install PySocks:
```bash
pip3 install PySocks
```

### SSL Certificate Errors

If you encounter SSL errors behind a proxy:
```bash
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

## License

MIT License - Same as the original PHP version

## Credits

- Original PHP version by Jay MOULIN
- Python port maintains the same architecture and philosophy
