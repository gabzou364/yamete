"""Parser for identifying and routing URLs to appropriate drivers."""

import os
import importlib
import inspect
from typing import List, Optional
from yamete.driver_interface import DriverInterface
from yamete.result_iterator import ResultIterator


class Parser:
    """Parser that routes URLs to appropriate drivers."""
    
    def __init__(self):
        """Initialize parser with built-in drivers."""
        self.drivers: List[DriverInterface] = []
        self._load_builtin_drivers()
    
    def _load_builtin_drivers(self):
        """Load all built-in drivers from drivers directory."""
        drivers_dir = os.path.join(os.path.dirname(__file__), 'drivers')
        
        if not os.path.exists(drivers_dir):
            return
        
        for filename in os.listdir(drivers_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'yamete.drivers.{module_name}')
                    
                    # Find all classes that inherit from DriverInterface
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, DriverInterface) and 
                            obj is not DriverInterface and
                            obj.__module__ == module.__name__):
                            self.drivers.append(obj())
                except Exception as e:
                    print(f"Warning: Failed to load driver {module_name}: {e}")
    
    def add_driver_directory(self, directory: str):
        """
        Add custom drivers from a directory.
        
        Args:
            directory: Path to directory containing driver files
        """
        if not os.path.isdir(directory):
            raise ValueError(f"{directory} is not a valid directory")
        
        import sys
        sys.path.insert(0, directory)
        
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(module_name)
                    
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, DriverInterface) and 
                            obj is not DriverInterface):
                            driver = obj()
                            if driver not in self.drivers:
                                self.drivers.append(driver)
                except Exception as e:
                    print(f"Warning: Failed to load custom driver {module_name}: {e}")
    
    def parse(self, url: str, downloads_dir: str = "downloads") -> Optional[ResultIterator]:
        """
        Parse URL and return result iterator if a matching driver is found.
        
        Args:
            url: URL to parse
            downloads_dir: Base directory for downloads
            
        Returns:
            ResultIterator if driver found, None otherwise
        """
        for driver in self.drivers:
            driver.clean().set_url(url)
            if driver.can_handle():
                return ResultIterator(driver, downloads_dir)
        
        return None
