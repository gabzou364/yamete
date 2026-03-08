#!/usr/bin/env python3
"""Simple test script for yamete Python CLI."""

import re
import sys
sys.path.insert(0, 'python')

from yamete.parser import Parser
from yamete.drivers.hdporncomics import HDPornComics

def test_driver_loading():
    """Test that drivers are loaded."""
    print("Testing driver loading...")
    parser = Parser()
    # We expect at least 3 production drivers (may have more from example_driver.py)
    assert len(parser.drivers) >= 3, f"Expected at least 3 drivers, got {len(parser.drivers)}"
    
    # Check that the key drivers are present
    driver_names = [d.__class__.__name__ for d in parser.drivers]
    required_drivers = ['HDPornComics', 'NHentai', 'EHentai']
    for req_driver in required_drivers:
        assert req_driver in driver_names, f"Required driver {req_driver} not found"
    
    print(f"✓ Loaded {len(parser.drivers)} drivers (including {', '.join(required_drivers)})")
    return True

def test_hdporncomics_pattern():
    """Test HDPornComics URL pattern matching."""
    print("\nTesting HDPornComics driver...")
    driver = HDPornComics()
    
    # Test valid URL
    driver.set_url("https://hdporncomics.com/example-album/")
    assert driver.can_handle(), "Should handle hdporncomics.com URL"
    print("✓ Correctly handles valid URL")
    
    # Test invalid URL
    driver.set_url("https://example.com/something/")
    assert not driver.can_handle(), "Should not handle non-hdporncomics URL"
    print("✓ Correctly rejects invalid URL")
    
    return True

def test_nhentai_pattern():
    """Test NHentai URL pattern matching."""
    print("\nTesting NHentai driver...")
    from yamete.drivers.nhentai import NHentai
    driver = NHentai()
    
    # Test valid URL
    driver.set_url("https://nhentai.net/g/123456/")
    assert driver.can_handle(), "Should handle nhentai.net URL"
    print("✓ Correctly handles valid URL")
    
    # Test invalid URL
    driver.set_url("https://example.com/something/")
    assert not driver.can_handle(), "Should not handle non-nhentai URL"
    print("✓ Correctly rejects invalid URL")
    
    return True

def test_ehentai_pattern():
    """Test EHentai URL pattern matching."""
    print("\nTesting EHentai driver...")
    from yamete.drivers.ehentai import EHentai
    driver = EHentai()
    
    # Test valid URL
    driver.set_url("https://e-hentai.org/g/123456/abcdef1234/")
    assert driver.can_handle(), "Should handle e-hentai.org URL"
    print("✓ Correctly handles valid URL")
    
    # Test exhentai URL
    driver.set_url("https://exhentai.org/g/123456/abcdef1234/")
    assert driver.can_handle(), "Should handle exhentai.org URL"
    print("✓ Correctly handles exhentai URL")
    
    # Test invalid URL
    driver.set_url("https://example.com/something/")
    assert not driver.can_handle(), "Should not handle non-ehentai URL"
    print("✓ Correctly rejects invalid URL")
    
    return True

def test_parser_routing():
    """Test that parser routes URLs to correct drivers."""
    print("\nTesting parser URL routing...")
    parser = Parser()
    
    # We test by checking can_handle directly instead of calling parse
    # (which would try to fetch the page)
    
    # Test HDPornComics routing
    found = False
    for driver in parser.drivers:
        driver.set_url("https://hdporncomics.com/test-album/")
        if driver.can_handle():
            found = True
            break
    assert found, "Parser should find handler for hdporncomics"
    print("✓ Correctly routes hdporncomics.com URL")
    
    # Test NHentai routing
    found = False
    for driver in parser.drivers:
        driver.set_url("https://nhentai.net/g/123456/")
        if driver.can_handle():
            found = True
            break
    assert found, "Parser should find handler for nhentai"
    print("✓ Correctly routes nhentai.net URL")
    
    # Test EHentai routing
    found = False
    for driver in parser.drivers:
        driver.set_url("https://e-hentai.org/g/123456/abcdef1234/")
        if driver.can_handle():
            found = True
            break
    assert found, "Parser should find handler for ehentai"
    print("✓ Correctly routes e-hentai.org URL")
    
    # Test unknown URL
    found = False
    for driver in parser.drivers:
        driver.set_url("https://unknown-site.com/gallery/")
        if driver.can_handle():
            found = True
            break
    assert not found, "Parser should not find handler for unknown URL"
    print("✓ Correctly returns no handler for unknown URL")
    
    return True

def test_get_session_creates_session():
    """Test that get_session() without proxies creates a session."""
    print("\nTesting get_session() creates session...")
    driver = HDPornComics()

    assert driver.session is None, "Session should be None initially"
    session = driver.get_session()
    assert session is not None, "get_session() should return a session"
    assert driver.session is session, "Session should be stored on the driver"
    print("✓ get_session() creates a new session")
    return True


def test_get_session_sets_browser_headers():
    """Test that get_session() sets full browser-like headers to avoid 403 errors."""
    print("\nTesting get_session() sets browser-like headers...")
    driver = HDPornComics()

    session = driver.get_session()
    headers = session.headers

    assert re.search(r'Chrome/\d+', headers.get('User-Agent', '')), "User-Agent should contain a Chrome version"
    assert 'Accept' in headers, "Accept header should be set"
    assert 'Accept-Language' in headers, "Accept-Language header should be set"
    assert 'Accept-Encoding' in headers, "Accept-Encoding header should be set"
    assert 'Sec-Fetch-Dest' in headers, "Sec-Fetch-Dest header should be set"
    assert 'Sec-Fetch-Mode' in headers, "Sec-Fetch-Mode header should be set"
    print("✓ get_session() sets complete browser-like headers")
    return True


def test_get_session_updates_proxies_on_existing_session():
    """Test that get_session(proxies=...) updates proxies even if session already exists."""
    print("\nTesting get_session(proxies=...) updates existing session proxies...")
    driver = HDPornComics()

    # Create session first (without proxies)
    session = driver.get_session()
    assert session.proxies.get('http') is None, "Should have no http proxy initially"

    # Now apply proxies to the existing session
    proxy_dict = {'http': 'http://proxy:8080', 'https': 'http://proxy:8080'}
    session2 = driver.get_session(proxies=proxy_dict)

    assert session2 is session, "Should return the same session object"
    assert session2.proxies.get('http') == 'http://proxy:8080', "http proxy should be updated"
    assert session2.proxies.get('https') == 'http://proxy:8080', "https proxy should be updated"
    print("✓ get_session(proxies=...) updates proxies on existing session")
    return True


def test_get_session_sets_proxies_on_new_session():
    """Test that get_session(proxies=...) sets proxies when creating a new session."""
    print("\nTesting get_session(proxies=...) sets proxies on new session...")
    driver = HDPornComics()

    proxy_dict = {'http': 'http://proxy:9090', 'https': 'http://proxy:9090'}
    session = driver.get_session(proxies=proxy_dict)

    assert session is not None, "get_session() should return a session"
    assert session.proxies.get('http') == 'http://proxy:9090', "http proxy should be set"
    assert session.proxies.get('https') == 'http://proxy:9090', "https proxy should be set"
    print("✓ get_session(proxies=...) sets proxies on new session")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Yamete Python CLI - Test Suite")
    print("=" * 60)
    
    tests = [
        test_driver_loading,
        test_hdporncomics_pattern,
        test_nhentai_pattern,
        test_ehentai_pattern,
        test_parser_routing,
        test_get_session_creates_session,
        test_get_session_sets_browser_headers,
        test_get_session_updates_proxies_on_existing_session,
        test_get_session_sets_proxies_on_new_session,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
