#!/usr/bin/env python3
"""Yamete CLI - Main command-line interface."""

import argparse
import os
import sys
from typing import List, Optional, Dict
from yamete.parser import Parser
from yamete.result_iterator import ResultIterator
from yamete.pdf_converter import PDFConverter
from yamete.zip_archiver import ZipArchiver


VERSION = "2.0.0"


def parse_proxy(proxy_string: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Parse proxy string into dict for requests.
    
    Args:
        proxy_string: Proxy string like "http://proxy:port" or "socks5://proxy:port"
        
    Returns:
        Dict with http and https proxy settings
    """
    if not proxy_string:
        return None
    
    return {
        'http': proxy_string,
        'https': proxy_string
    }


def download_url(url: str, parser: Parser, args, error_file=None) -> bool:
    """
    Download a single URL.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        url = url.strip()
        if not url:
            return True
        
        print(f"\033[93mParsing {url}\033[0m")
        
        result = parser.parse(url, args.downloads_dir)
        
        if not result:
            error_msg = (
                f"Unable to parse {url}.\n"
                "Consider creating an issue on https://github.com/jaymoulin/yamete/issues/"
            )
            raise RuntimeError(error_msg)
        
        # Download all files
        downloaded_files = []
        total = len(result)
        
        if args.verbose:
            print(f"Downloading {total} files...")
        
        for idx, downloadable in enumerate(result):
            if args.verbose:
                print(f"[{idx + 1}/{total}] Downloading {downloadable.get_url()} > {downloadable.get_path()}")
            
            try:
                response = downloadable.download()
                if response.status_code != 200:
                    print(f"\033[91mDownload error: {downloadable.get_url()} (Status: {response.status_code})\033[0m")
                else:
                    downloaded_files.append(downloadable.get_path())
            except Exception as e:
                print(f"\033[91mDownload error: {downloadable.get_url()} - {e}\033[0m")
        
        if not downloaded_files:
            raise RuntimeError("No files were downloaded successfully")
        
        print(f"\033[92mDownload {url} success!\033[0m")
        
        # Get base folder for output
        if downloaded_files:
            base_folder = os.path.dirname(downloaded_files[0])
            base_name = os.path.basename(base_folder)
        
        # Create PDF if requested
        if args.pdf:
            print("\033[93mConverting to PDF\033[0m")
            try:
                pdf_converter = PDFConverter()
                pdf_converter.add_images(downloaded_files)
                pdf_path = os.path.join(os.path.dirname(base_folder), f"{base_name}.pdf")
                pdf_converter.create_pdf(pdf_path)
                
                # Clean up images
                for file_path in downloaded_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                if os.path.exists(base_folder) and not os.listdir(base_folder):
                    os.rmdir(base_folder)
                    
                print(f"\033[93mPDF created: {pdf_path}\033[0m")
            except Exception as e:
                print(f"\033[91mPDF error: {e}\033[0m")
        
        # Create ZIP if requested (and not PDF)
        elif args.zip:
            print("\033[93mCreating zip archive\033[0m")
            try:
                zip_path = os.path.join(os.path.dirname(base_folder), f"{base_name}.zip")
                ZipArchiver.create_zip_and_cleanup(downloaded_files, zip_path)
                print(f"\033[93mZip created: {zip_path}\033[0m")
            except Exception as e:
                print(f"\033[91mZip error: {e}\033[0m")
        
        return True
        
    except Exception as e:
        if error_file:
            error_file.write(url + '\n')
            error_file.flush()
        
        error_msg = str(e)
        print(f"\033[91m{error_msg}\033[0m")
        return False


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Yamete - Manga/Hentai downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Yamete {VERSION} - Jay MOULIN <https://twitter.com/MoulinJay>

Examples:
  yamete -u https://hdporncomics.com/example/
  yamete -l urls.txt -p
  yamete -i --proxy http://proxy:8080
  yamete -u https://nhentai.net/g/123456/ --zip
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-u', '--url', help='URL to download from')
    input_group.add_argument('-l', '--list', help='File with list of URLs (one per line)')
    input_group.add_argument('-i', '--interactive', action='store_true',
                            help='Interactive mode (read URLs from stdin)')
    
    # Optional features
    parser.add_argument('-p', '--pdf', action='store_true',
                       help='Create a PDF file instead of separate images')
    parser.add_argument('-z', '--zip', action='store_true',
                       help='Create a ZIP archive')
    parser.add_argument('-e', '--errors', help='File to write failed URLs')
    parser.add_argument('-d', '--drivers', action='append',
                       help='Directory with custom drivers (can be specified multiple times)')
    
    # Proxy support
    parser.add_argument('--proxy', help='Proxy URL (e.g., http://proxy:8080 or socks5://proxy:1080)')
    
    # Output options
    parser.add_argument('--downloads-dir', default='downloads',
                       help='Directory for downloads (default: downloads)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Quiet mode (minimal output)')
    parser.add_argument('--version', action='version', version=f'Yamete {VERSION}')
    
    args = parser.parse_args()
    
    # Create parser and load drivers
    url_parser = Parser()
    
    # Add custom drivers if specified
    if args.drivers:
        for driver_dir in args.drivers:
            try:
                url_parser.add_driver_directory(driver_dir)
            except Exception as e:
                print(f"\033[91mError loading drivers from {driver_dir}: {e}\033[0m")
    
    # Setup proxy if specified
    if args.proxy:
        proxy_dict = parse_proxy(args.proxy)
        # Set proxy for all drivers
        for driver in url_parser.drivers:
            driver.get_session(proxies=proxy_dict)
    
    # Open error file if specified
    error_file = None
    if args.errors:
        error_dir = os.path.dirname(args.errors)
        if error_dir and not os.path.exists(error_dir):
            os.makedirs(error_dir, exist_ok=True)
        error_file = open(args.errors, 'a')
    
    try:
        # Process URLs
        urls = []
        
        if args.url:
            urls = [args.url]
        elif args.list:
            if not os.path.isfile(args.list):
                print(f"\033[91mError: File not found: {args.list}\033[0m")
                return 1
            with open(args.list, 'r') as f:
                urls = f.readlines()
        elif args.interactive:
            print("\033[93m/!\\ INTERACTIVE MODE /!\\\n\nPress Ctrl+C or Ctrl+D to end\033[0m")
            try:
                while True:
                    line = input()
                    if line.strip():
                        download_url(line, url_parser, args, error_file)
            except (EOFError, KeyboardInterrupt):
                print("\n\033[92mExiting interactive mode\033[0m")
                return 0
        
        # Download all URLs
        success_count = 0
        fail_count = 0
        
        for url in urls:
            if download_url(url, url_parser, args, error_file):
                success_count += 1
            else:
                fail_count += 1
        
        if len(urls) > 1:
            print(f"\n\033[92mCompleted: {success_count} successful, {fail_count} failed\033[0m")
        
        return 0 if fail_count == 0 else 1
        
    finally:
        if error_file:
            error_file.close()


if __name__ == '__main__':
    sys.exit(main())
