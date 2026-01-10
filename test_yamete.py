#!/usr/bin/env python3
"""Simple test script for yamete Python CLI."""

import sys
sys.path.insert(0, 'python')

from yamete.parser import Parser
from yamete.drivers.hdporncomics import HDPornComics

def test_driver_loading():
    """Test that drivers are loaded."""
    print("Testing driver loading...")
    parser = Parser()
    assert len(parser.drivers) == 3, f"Expected 3 drivers, got {len(parser.drivers)}"
    print(f"✓ Loaded {len(parser.drivers)} drivers")
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
