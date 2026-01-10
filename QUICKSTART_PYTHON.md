# Yamete Python - Quick Start Guide

## Installation

### Option 1: Standalone Script (Recommended)

No installation needed! Just install dependencies and run:

```bash
# Install dependencies
pip3 install requests beautifulsoup4 Pillow reportlab

# Run directly
python3 yamete.py -u "https://hdporncomics.com/example-album/"
```

### Option 2: Install as Package

```bash
# Install with pip
pip3 install .

# Use yamete command
yamete -u "https://hdporncomics.com/example-album/"
```

### Option 3: Install with Proxy

If you're behind a proxy:

```bash
# Set proxy environment variables
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Install dependencies through proxy
pip3 install --proxy $HTTP_PROXY requests beautifulsoup4 Pillow reportlab

# Or use pip's proxy flag
pip3 install --proxy http://proxy.example.com:8080 -r requirements.txt
```

## Basic Usage

### Download a single album

```bash
python3 yamete.py -u "https://hdporncomics.com/example-album/"
```

Files will be saved to: `downloads/hdporncomics.com/example-album/`

### Download with proxy

```bash
python3 yamete.py -u "https://hdporncomics.com/example-album/" --proxy http://proxy:8080
```

### Create PDF instead of images

```bash
python3 yamete.py -u "https://hdporncomics.com/example-album/" -p
```

Creates: `downloads/example-album.pdf`

### Create ZIP archive

```bash
python3 yamete.py -u "https://hdporncomics.com/example-album/" -z
```

Creates: `downloads/example-album.zip`

### Download multiple URLs from file

Create a file `urls.txt`:
```
https://hdporncomics.com/album1/
https://hdporncomics.com/album2/
https://nhentai.net/g/123456/
```

Then run:
```bash
python3 yamete.py -l urls.txt
```

### Interactive mode

```bash
python3 yamete.py -i
```

Paste URLs one at a time, press Enter after each. Press Ctrl+D or Ctrl+C to exit.

### Verbose output

```bash
python3 yamete.py -u "https://hdporncomics.com/example-album/" -v
```

### Save failed URLs

```bash
python3 yamete.py -l urls.txt -e errors.txt
```

Failed URLs will be written to `errors.txt`.

## Supported Sites

Currently supported:
- ✅ **hdporncomics.com** (Primary driver)
- ✅ nhentai.net
- ✅ e-hentai.org / exhentai.org

More drivers can be easily added following the same pattern as the existing ones.

## Testing

Run the test suite to verify everything works:

```bash
python3 test_yamete.py
```

Expected output:
```
============================================================
Yamete Python CLI - Test Suite
============================================================
Testing driver loading...
✓ Loaded 3 drivers

Testing HDPornComics driver...
✓ Correctly handles valid URL
✓ Correctly rejects invalid URL

...

============================================================
Results: 5 passed, 0 failed
============================================================
```

## Troubleshooting

### Module not found errors

Install dependencies:
```bash
pip3 install -r requirements.txt
```

### Proxy issues with SOCKS

For SOCKS proxy support, install PySocks:
```bash
pip3 install PySocks
```

### SSL/Certificate errors behind proxy

```bash
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Permission denied on downloads directory

The script automatically creates the downloads directory. If you get permission errors:
```bash
mkdir downloads
chmod 755 downloads
```

Or use a custom download directory:
```bash
python3 yamete.py -u "https://example.com/album/" --downloads-dir /path/to/writable/dir
```

## Comparison: Python vs PHP Version

| Feature | PHP | Python |
|---------|-----|--------|
| **Installation** | Requires PHP, Composer | Requires Python, pip |
| **Dependencies** | Many (8+) | Minimal (4) |
| **Proxy Support** | ❌ No | ✅ Yes |
| **Ease of Use** | Medium | High |
| **Sites Supported** | 350+ | 3 (easily expandable) |

## Next Steps

- See [README_PYTHON.md](README_PYTHON.md) for complete documentation
- Check [test_yamete.py](test_yamete.py) for usage examples
- Add custom drivers by following the pattern in `python/yamete/drivers/`
