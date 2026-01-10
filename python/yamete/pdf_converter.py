"""PDF conversion utilities."""

import os
from typing import List
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image


class PDFConverter:
    """Convert images to PDF."""
    
    def __init__(self):
        self.images: List[str] = []
    
    def add_images(self, image_paths: List[str]):
        """Add images to be converted."""
        self.images.extend(image_paths)
    
    def create_pdf(self, output_path: str):
        """
        Create PDF from images.
        
        Args:
            output_path: Path to save the PDF
        """
        if not self.images:
            raise ValueError("No images to convert")
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=A4)
        a4_width, a4_height = A4
        
        for image_path in self.images:
            try:
                # Open image
                img = Image.open(image_path)
                img_width, img_height = img.size
                
                # Calculate scaling to fit A4
                width_ratio = a4_width / img_width
                height_ratio = a4_height / img_height
                ratio = min(width_ratio, height_ratio)
                
                new_width = img_width * ratio
                new_height = img_height * ratio
                
                # Determine page orientation
                if img_width > img_height:
                    c.setPageSize((a4_height, a4_width))
                    c.drawImage(image_path, 0, 0, width=a4_height, height=a4_width, preserveAspectRatio=True)
                else:
                    c.setPageSize(A4)
                    c.drawImage(image_path, 0, 0, width=new_width, height=new_height, preserveAspectRatio=True)
                
                c.showPage()
                
            except Exception as e:
                print(f"Warning: Failed to add {image_path} to PDF: {e}")
                continue
        
        c.save()
        print(f"PDF created: {output_path}")
