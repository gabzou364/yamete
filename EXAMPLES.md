# Yamete Python CLI - Usage Examples

This document provides real-world usage examples for the Yamete Python CLI.

## Table of Contents
1. [Basic Usage](#basic-usage)
2. [Batch Operations](#batch-operations)
3. [Proxy Configuration](#proxy-configuration)
4. [Output Formats](#output-formats)
5. [Advanced Scenarios](#advanced-scenarios)

## Basic Usage

### Download a single gallery

```bash
python3 yamete.py -u "https://hdporncomics.com/example-album/"
```

Output:
```
Parsing https://hdporncomics.com/example-album/
Downloading 25 files...
Download https://hdporncomics.com/example-album/ success!
```

Files saved to: `downloads/hdporncomics.com/example-album/`

### Download with verbose output

```bash
python3 yamete.py -u "https://hdporncomics.com/example-album/" -v
```

Output:
```
Parsing https://hdporncomics.com/example-album/
Downloading 25 files...
[1/25] Downloading https://cdn.example.com/img1.jpg > downloads/hdporncomics.com/example-album/00001.jpg
[2/25] Downloading https://cdn.example.com/img2.jpg > downloads/hdporncomics.com/example-album/00002.jpg
...
Download https://hdporncomics.com/example-album/ success!
```

## Batch Operations

### Download from a list of URLs

Create `urls.txt`:
```
https://hdporncomics.com/album-1/
https://hdporncomics.com/album-2/
https://nhentai.net/g/123456/
https://e-hentai.org/g/789012/abcdef1234/
```

Run:
```bash
python3 yamete.py -l urls.txt -v
```

### Track failed downloads

```bash
python3 yamete.py -l urls.txt -e failed.txt
```

If any downloads fail, their URLs will be saved to `failed.txt` for retry later:
```bash
# Retry failed downloads
python3 yamete.py -l failed.txt
```

### Interactive mode for on-the-fly downloading

```bash
python3 yamete.py -i
```

Then paste URLs one at a time:
```
/!\ INTERACTIVE MODE /!\

Send ^C or EOF to end
https://hdporncomics.com/album-1/
Parsing https://hdporncomics.com/album-1/
Download https://hdporncomics.com/album-1/ success!
https://hdporncomics.com/album-2/
Parsing https://hdporncomics.com/album-2/
Download https://hdporncomics.com/album-2/ success!
^C
Exiting interactive mode
```

## Proxy Configuration

### Using HTTP proxy

```bash
python3 yamete.py -u "https://hdporncomics.com/example/" --proxy http://proxy.example.com:8080
```

### Using authenticated proxy

```bash
python3 yamete.py -u "https://hdporncomics.com/example/" --proxy http://user:pass@proxy.example.com:8080
```

### Using SOCKS proxy (requires PySocks)

```bash
pip3 install PySocks
python3 yamete.py -u "https://hdporncomics.com/example/" --proxy socks5://proxy.example.com:1080
```

### Batch download through proxy

```bash
python3 yamete.py -l urls.txt --proxy http://proxy.example.com:8080 -v
```

## Output Formats

### Create PDF from downloaded images

```bash
python3 yamete.py -u "https://hdporncomics.com/example/" -p
```

Output:
```
Parsing https://hdporncomics.com/example/
Downloading 25 files...
Download https://hdporncomics.com/example/ success!
Converting to PDF
PDF created: downloads/example.pdf
```

Original images are automatically deleted after PDF creation.

### Create ZIP archive

```bash
python3 yamete.py -u "https://hdporncomics.com/example/" -z
```

Output:
```
Parsing https://hdporncomics.com/example/
Downloading 25 files...
Download https://hdporncomics.com/example/ success!
Creating zip archive
ZIP created: downloads/example.zip
```

Original images are automatically deleted after ZIP creation.

### Batch PDF creation

```bash
python3 yamete.py -l urls.txt -p
```

Each gallery will be converted to its own PDF file.

## Advanced Scenarios

### Custom download directory

```bash
python3 yamete.py -u "https://hdporncomics.com/example/" --downloads-dir /mnt/external/manga
```

### Using custom drivers

Create custom driver in `/home/user/custom-drivers/mysite.py`:
```python
from yamete.driver_interface import DriverInterface
# ... driver implementation
```

Use it:
```bash
python3 yamete.py -u "https://mysite.com/gallery/123/" -d /home/user/custom-drivers
```

### Multiple custom driver directories

```bash
python3 yamete.py -u "https://example.com/gallery/" \
    -d /path/to/drivers1 \
    -d /path/to/drivers2 \
    -v
```

### Automated daily download script

Create `daily_download.sh`:
```bash
#!/bin/bash

# Daily download script
DATE=$(date +%Y%m%d)
LOG_FILE="logs/yamete_${DATE}.log"
ERROR_FILE="logs/errors_${DATE}.txt"

mkdir -p logs

python3 yamete.py \
    -l daily_urls.txt \
    -e "$ERROR_FILE" \
    --downloads-dir "/mnt/storage/manga" \
    -v \
    > "$LOG_FILE" 2>&1

# If there were errors, send notification
if [ -s "$ERROR_FILE" ]; then
    echo "Some downloads failed. Check $ERROR_FILE"
fi
```

Make it executable:
```bash
chmod +x daily_download.sh
```

Add to crontab for daily execution:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/daily_download.sh
```

### Parallel downloading (using GNU parallel)

For very large lists, you can parallelize:

```bash
# Split URLs into chunks
split -l 10 urls.txt url_chunk_

# Download in parallel (4 at a time)
ls url_chunk_* | parallel -j 4 python3 yamete.py -l {} -e errors_{}.txt

# Combine error files
cat errors_*.txt > all_errors.txt

# Cleanup chunk files
rm url_chunk_* errors_*.txt
```

### Integration with other tools

Download and immediately convert to CBZ format:
```bash
python3 yamete.py -u "https://hdporncomics.com/example/" -z
mv downloads/example.zip downloads/example.cbz
```

Download through proxy and create PDF:
```bash
python3 yamete.py \
    -l urls.txt \
    --proxy http://proxy:8080 \
    -p \
    -e failed.txt \
    -v
```

### Quiet mode for scripts

For use in scripts where you only want errors:
```bash
python3 yamete.py -l urls.txt -q 2>errors.log
if [ $? -ne 0 ]; then
    echo "Download failed, check errors.log"
fi
```

## Comparison Table

| Task | PHP Version | Python Version |
|------|-------------|----------------|
| Simple download | `php download -u <url>` | `python3 yamete.py -u <url>` |
| With proxy | Not supported | `python3 yamete.py -u <url> --proxy <proxy>` |
| Create PDF | `php download -u <url> -p` | `python3 yamete.py -u <url> -p` |
| Batch download | `php download -l urls.txt` | `python3 yamete.py -l urls.txt` |
| Custom drivers | `php download -u <url> -d /path` | `python3 yamete.py -u <url> -d /path` |

## Tips

1. **Always test with a single URL first** before batch downloading
2. **Use `-v` flag** when debugging to see detailed progress
3. **Keep error logs** with `-e` flag for large batch operations
4. **Use proxies** if you're downloading large amounts to avoid IP blocks
5. **Create PDFs or ZIPs** to save disk space and organize content
6. **Set up cron jobs** for automated regular downloads
7. **Monitor disk space** when doing large batch downloads
8. **Test custom drivers** with various URLs before using in production
