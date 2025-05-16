import os
import sys
from PIL import Image, ImageFilter
from typing import Tuple, Optional, Literal
import logging

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

from app.core.config import settings

logger = logging.getLogger(__name__)

class BackgroundProcessor:
    def __init__(self):
        self.supported_sharpen_methods = ['sharpen', 'unsharp']
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """Ensure output directory exists"""
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

    def sharpen_image(self, image: Image.Image, method: Literal['sharpen', 'unsharp'] = 'sharpen') -> Image.Image:
        """
        Apply sharpening to the image using the specified method.
        
        Args:
            image: PIL Image to sharpen
            method: Sharpening method ('sharpen' or 'unsharp')
            
        Returns:
            Sharpened PIL Image
            
        Raises:
            ValueError: If unsupported sharpen method is provided
        """
        if method not in self.supported_sharpen_methods:
            raise ValueError(f"Unsupported sharpen method. Supported methods: {self.supported_sharpen_methods}")
            
        if method == 'sharpen':
            return image.filter(ImageFilter.SHARPEN)
        else:  # unsharp
            return image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

    def calculate_target_dimensions(
        self, 
        image_size: Tuple[int, int], 
        target_ratio: float
    ) -> Tuple[int, int]:
        """
        Calculate target dimensions while maintaining aspect ratio.
        
        Args:
            image_size: Original image dimensions (width, height)
            target_ratio: Target aspect ratio (width/height)
            
        Returns:
            Tuple of (target_width, target_height)
        """
        iw, ih = image_size
        orig_ratio = iw / ih
        
        if orig_ratio > target_ratio:
            # Image is too wide, increase height
            target_h = int(iw / target_ratio)
            return iw, target_h
        else:
            # Image is too tall, increase width
            target_w = int(ih * target_ratio)
            return target_w, ih

    def add_background(
        self,
        image_path: str,
        background_color: Tuple[int, int, int],
        output_path: str,
        target_aspect_ratio: Optional[Tuple[int, int]] = None,
        sharpen_method: Optional[Literal['sharpen', 'unsharp']] = None
    ) -> None:
        """
        Add background to image and optionally adjust aspect ratio.
        
        Args:
            image_path: Path to input image
            background_color: RGB background color tuple
            output_path: Path to save output image
            target_aspect_ratio: Optional target aspect ratio (width, height)
            sharpen_method: Optional sharpening method to apply
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        try:
            # Open and convert image to RGBA
            image = Image.open(image_path).convert("RGBA")
            
            # Apply sharpening if method specified
            if sharpen_method:
                image = self.sharpen_image(image, method=sharpen_method)
            
            if not target_aspect_ratio:
                logger.info("No target aspect ratio set, using original size")
                background = Image.new("RGBA", image.size, background_color)
                background.paste(image, (0, 0), image)
            else:
                # Calculate target dimensions
                target_ratio = target_aspect_ratio[0] / target_aspect_ratio[1]
                target_w, target_h = self.calculate_target_dimensions(image.size, target_ratio)
                
                logger.info(f"Original ratio: {image.size[0]/image.size[1]:.2f}, "
                          f"Target ratio: {target_ratio:.2f}")
                
                # Create new background with target dimensions
                background = Image.new("RGBA", (target_w, target_h), background_color)
                
                # Calculate centering coordinates
                x = (target_w - image.size[0]) // 2
                y = (target_h - image.size[1]) // 2
                
                background.paste(image, (x, y), image)
            
            # Convert to RGB and save
            final_image = background.convert("RGB")
            final_image.save(output_path)
            logger.info(f"Image saved successfully to {output_path}")
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise

def main():
    """Example usage of BackgroundProcessor"""
    processor = BackgroundProcessor()
    base_path = os.path.join(project_root, "output-images")
    # Example configurations
    test_configs = [
        {
            "image_path": os.path.join(base_path, "tt18_segmented.png"),
            "background_color": (255, 255, 255),
            "output_path": os.path.join(base_path, "tt18_segmented_white_bg_9_16.jpg"),
            "target_aspect_ratio": (9, 16)
        }
    ]
    
    # Process each configuration
    for config in test_configs:
        processor.add_background(
            image_path=config["image_path"],
            background_color=config["background_color"],
            output_path=config["output_path"],
            target_aspect_ratio=config["target_aspect_ratio"],
            sharpen_method='unsharp'
        )

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
