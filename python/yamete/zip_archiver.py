"""ZIP archive utilities."""

import os
import zipfile
from typing import List


class ZipArchiver:
    """Create ZIP archives from downloaded files."""
    
    @staticmethod
    def create_zip(file_paths: List[str], output_path: str):
        """
        Create a ZIP archive from files.
        
        Args:
            file_paths: List of file paths to include
            output_path: Path to save the ZIP file
        """
        if not file_paths:
            raise ValueError("No files to archive")
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    # Add file with relative path
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname)
        
        print(f"ZIP created: {output_path}")
    
    @staticmethod
    def create_zip_and_cleanup(file_paths: List[str], output_path: str):
        """
        Create a ZIP archive and remove original files.
        
        Args:
            file_paths: List of file paths to include
            output_path: Path to save the ZIP file
        """
        ZipArchiver.create_zip(file_paths, output_path)
        
        # Remove original files
        folders_to_remove = set()
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
                folders_to_remove.add(os.path.dirname(file_path))
        
        # Remove empty folders
        for folder in folders_to_remove:
            try:
                if os.path.exists(folder) and not os.listdir(folder):
                    os.rmdir(folder)
            except Exception:
                pass
