# Yamete Python CLI - Architecture

This document describes the architecture of the Python CLI implementation.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        yamete.py                             │
│                    (Entry Point)                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                        cli.py                                │
│              (Command-Line Interface)                        │
│  • Parse arguments (argparse)                                │
│  • Handle input modes (URL/file/interactive)                 │
│  • Manage output formats (images/PDF/ZIP)                    │
│  • Error logging                                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      parser.py                               │
│                   (URL Router)                               │
│  • Load all available drivers                                │
│  • Route URLs to appropriate drivers                         │
│  • Return ResultIterator                                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
         ┌──────────────┴──────────────┐
         │                             │
         ▼                             ▼
┌──────────────────┐         ┌──────────────────┐
│ driver_interface │         │  result_iterator │
│   (Base Class)   │◄────────│   (Iterator)     │
│  • HTTP Session  │         │  • Iterate files │
│  • Proxy Support │         │  • File paths    │
│  • can_handle()  │         └──────────────────┘
│  • downloadables │                 │
└────────┬─────────┘                 │
         │                           │
         ▼                           ▼
┌─────────────────┐         ┌──────────────────┐
│    drivers/     │         │  downloadable.py │
│  ├─hdporncomics│         │  (File Download) │
│  ├─nhentai     │         │  • download()    │
│  ├─ehentai     │         │  • get_path()    │
│  └─custom...   │         │  • get_url()     │
└─────────────────┘         └──────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
          ┌─────────────┐   ┌─────────────┐  ┌─────────────┐
          │pdf_converter│   │zip_archiver │  │ File System │
          │  (PDF Gen)  │   │  (Archive)  │  │  (Storage)  │
          └─────────────┘   └─────────────┘  └─────────────┘
```

## Component Breakdown

### 1. Entry Point (yamete.py)
- Standalone script that can be run without installation
- Sets up Python path to include `python/` directory
- Delegates to CLI module

### 2. CLI (cli.py)
Main command-line interface that:
- Parses command-line arguments using argparse
- Handles three input modes:
  - Single URL (`-u`)
  - File list (`-l`)
  - Interactive stdin (`-i`)
- Manages proxy configuration
- Coordinates download and conversion operations
- Handles error logging to file

### 3. Parser (parser.py)
URL routing system that:
- Automatically discovers and loads all drivers from `drivers/` directory
- Can load custom drivers from external directories
- Routes URLs to appropriate drivers via `can_handle()` method
- Returns ResultIterator for matched URLs

### 4. Driver Interface (driver_interface.py)
Abstract base class that defines:
- Required methods: `can_handle()`, `get_downloadables()`
- HTTP session management with proxy support
- Common utilities (User-Agent, session cleanup)
- Template for all driver implementations

### 5. Drivers (drivers/*.py)
Site-specific implementations:
- **HDPornComics**: Primary driver for hdporncomics.com
- **NHentai**: Driver for nhentai.net
- **EHentai**: Driver for e-hentai.org/exhentai.org
- Each driver:
  - Matches URL patterns
  - Parses HTML to extract image URLs
  - Returns dict of {filepath: download_url}

### 6. Result Iterator (result_iterator.py)
Iterable wrapper that:
- Wraps driver's downloadables dict
- Creates Downloadable objects on iteration
- Manages download directory paths
- Provides count and item access

### 7. Downloadable (downloadable.py)
Represents a single file to download:
- Stores path and URL
- Uses driver's HTTP session
- Implements streaming download
- Creates directories as needed

### 8. Output Processors
- **PDF Converter** (pdf_converter.py): Converts images to PDF using reportlab
- **ZIP Archiver** (zip_archiver.py): Creates ZIP archives and cleans up

## Data Flow

### Single URL Download Flow
```
1. User runs: python3 yamete.py -u "https://hdporncomics.com/album/"
2. CLI parses arguments, creates Parser
3. Parser loads all drivers (HDPornComics, NHentai, EHentai)
4. Parser.parse(url) calls each driver's can_handle()
5. HDPornComics.can_handle() returns True (URL matches)
6. HDPornComics.get_downloadables() fetches page and extracts URLs
7. Returns: {"hdporncomics.com/album/00001.jpg": "https://cdn.../img1.jpg", ...}
8. ResultIterator wraps the downloadables dict
9. CLI iterates over ResultIterator:
   - Creates Downloadable for each item
   - Calls Downloadable.download()
   - Downloads file to disk
10. All files downloaded to downloads/hdporncomics.com/album/
```

### Batch Download with PDF
```
1. User runs: python3 yamete.py -l urls.txt -p
2. CLI reads URLs from file
3. For each URL:
   - Parse and download (as above)
   - Collect file paths
4. After all downloads complete:
   - PDFConverter.create_pdf(files)
   - Convert images to PDF
   - Delete original images
5. Result: downloads/album.pdf
```

### Interactive Mode with Proxy
```
1. User runs: python3 yamete.py -i --proxy http://proxy:8080
2. CLI enters interactive mode
3. Parser loads drivers, sets proxy on all sessions
4. User enters URL via stdin
5. Download proceeds through proxy
6. Repeat until Ctrl+C or EOF
```

## Driver Architecture

### Creating a New Driver

```python
from yamete.driver_interface import DriverInterface
import re
from bs4 import BeautifulSoup

class MySite(DriverInterface):
    DOMAIN = 'mysite.com'
    
    def can_handle(self) -> bool:
        """Return True if URL matches this site."""
        pattern = rf'^https?://{re.escape(self.DOMAIN)}/gallery/(\d+)'
        return bool(re.match(pattern, self.url))
    
    def get_downloadables(self) -> dict:
        """Return {filepath: url} dict of downloads."""
        session = self.get_session()  # Has proxy if configured
        response = session.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        downloads = {}
        for idx, img in enumerate(soup.find_all('img', class_='gallery-img')):
            url = img['src']
            path = f"{self.DOMAIN}/gallery/{idx:05d}.jpg"
            downloads[path] = url
        
        return downloads
```

The driver is automatically discovered and loaded by the Parser.

## Session Management

### HTTP Session Flow
```
Driver created
    │
    ├─► get_session() called
    │       │
    │       ├─► Session doesn't exist?
    │       │       │
    │       │       ├─► Create new Session
    │       │       ├─► Set User-Agent
    │       │       └─► Apply proxy if configured
    │       │
    │       └─► Return session
    │
    ├─► download() uses session
    │       │
    │       └─► Streaming download (8KB chunks)
    │
    └─► clean() called
            │
            └─► Close session, free memory
```

## Error Handling

### Error Flow
```
Download URL
    │
    ├─► Try: Parse URL
    │       │
    │       ├─► Success: Continue
    │       └─► Failure: Log error, continue to next
    │
    ├─► Try: Download files
    │       │
    │       ├─► Success: Continue
    │       └─► Failure: Log error, mark as failed
    │
    └─► Error logging enabled?
            │
            ├─► Yes: Write failed URL to error file
            └─► No: Print error message
```

## Proxy Integration

### Proxy Setup
```
CLI argument: --proxy http://proxy:8080
    │
    ├─► Parse proxy string
    │
    ├─► Create proxy dict: {
    │       'http': 'http://proxy:8080',
    │       'https': 'http://proxy:8080'
    │   }
    │
    ├─► For each driver:
    │       │
    │       └─► driver.get_session(proxies=proxy_dict)
    │               │
    │               └─► Session configured with proxy
    │
    └─► All downloads use proxied sessions
```

## Key Design Decisions

### 1. Driver Pattern
**Why:** Extensibility - easy to add new sites without modifying core code
**How:** Abstract base class + automatic driver discovery

### 2. Minimal Dependencies
**Why:** Easy installation and deployment
**How:** Only 4 essential packages, no optional dependencies

### 3. Standalone Script
**Why:** Can run without installation
**How:** yamete.py sets up path and imports from python/ directory

### 4. Proxy Support
**Why:** Required feature for accessing content through proxies
**How:** Built into requests.Session, configured per driver

### 5. Streaming Downloads
**Why:** Memory efficient for large files
**How:** requests with stream=True, chunk iteration

### 6. Session Reuse
**Why:** Performance - avoid connection overhead
**How:** Single session per driver, reused for all downloads

### 7. Iterator Pattern
**Why:** Memory efficient, natural Python idiom
**How:** ResultIterator wraps dict, yields Downloadables

## Testing Strategy

### Test Coverage
```
test_yamete.py
    │
    ├─► Test: Driver loading
    │       └─► Verify 3 drivers loaded
    │
    ├─► Test: URL pattern matching
    │       ├─► HDPornComics URLs
    │       ├─► NHentai URLs
    │       └─► EHentai URLs
    │
    └─► Test: Parser routing
            └─► Verify correct driver selected for each URL
```

### Test Execution
```bash
python3 test_yamete.py
# Output: 5 tests, all passing
```

## Performance Characteristics

- **Memory:** O(1) for downloads (streaming), O(n) for PDF/ZIP
- **Network:** Concurrent connections via session reuse
- **Disk:** Sequential writes, directories created on-demand
- **CPU:** Minimal - mostly I/O bound

## Security Considerations

1. **Input Validation:** URL patterns validated before processing
2. **Path Traversal:** File paths sanitized, constrained to downloads dir
3. **Session Cleanup:** Resources freed after use
4. **Error Handling:** Exceptions caught, logged safely
5. **No Code Execution:** HTML parsing only, no eval/exec
6. **Dependency Scanning:** All dependencies from trusted sources

## Extensibility Points

1. **New Drivers:** Add to `python/yamete/drivers/`
2. **Custom Parsers:** Subclass DriverInterface
3. **Output Formats:** Add new converter classes
4. **CLI Options:** Extend argparse configuration
5. **Session Middleware:** Customize get_session()

This architecture provides a clean, maintainable, and extensible foundation for the Yamete Python CLI.
