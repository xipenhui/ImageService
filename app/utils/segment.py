import os
import base64
import requests
import logging
from typing import Tuple, Optional
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

from app.core.config import settings

logger = logging.getLogger(__name__)

class SegmentationService:
    def __init__(self):
        self.api_url = settings.SEGMENTATION_API_URL
        self.timeout = settings.API_TIMEOUT
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """Ensure output directory exists"""
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

    def _encode_image_to_base64(self, image_path: str) -> Tuple[bool, str]:
        """
        Encode image file to base64 string
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (success, result)
        """
        try:
            with open(image_path, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode("utf-8")
            logger.info("Image successfully encoded to Base64")
            return True, image_b64
        except Exception as e:
            error_msg = f"Failed to read image: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _decode_base64_response(self, b64_result: str) -> Tuple[bool, bytes]:
        """
        Decode base64 response from API
        
        Args:
            b64_result: Base64 encoded string from API
            
        Returns:
            Tuple of (success, decoded_bytes)
        """
        try:
            if ',' in b64_result:
                b64_result = b64_result.split(',', 1)[1]
            image_bytes = base64.b64decode(b64_result)
            logger.info("Successfully decoded API response")
            return True, image_bytes
        except Exception as e:
            error_msg = f"Failed to decode API response: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _save_processed_image(self, image_bytes: bytes, output_path: str) -> Tuple[bool, str]:
        """
        Save processed image to file
        
        Args:
            image_bytes: Image data in bytes
            output_path: Path to save the image
            
        Returns:
            Tuple of (success, result)
        """
        try:
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            logger.info(f"Processed image saved to: {output_path}")
            return True, output_path
        except Exception as e:
            error_msg = f"Failed to save processed image: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def segment_image(
        self, 
        image_path: str, 
        output_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Process image through segmentation API
        
        Args:
            image_path: Path to input image
            output_name: Optional name for output file
            
        Returns:
            Tuple of (success, result)
        """
        logger.info(f"Starting image processing: {image_path}")

        # Validate input file
        if not os.path.isfile(image_path):
            error_msg = f"File not found: {image_path}"
            logger.error(error_msg)
            return False, error_msg

        # Encode image to base64
        success, result = self._encode_image_to_base64(image_path)
        if not success:
            return False, result
        image_b64 = result

        # Prepare API request
        payload = {
            "image_base64": image_b64,
            "output_path": ""  # Required by server
        }

        # Send request to API
        try:
            logger.info(f"Sending request to API: {self.api_url}")
            response = requests.post(
                self.api_url, 
                json=payload, 
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"API request successful, status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        # Process API response
        try:
            data = response.json()
            b64_result = data.get("result_base64")
            if not b64_result:
                error_msg = "result_base64 field not found in response"
                logger.error(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"Failed to process API response: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        # Decode base64 response
        success, result = self._decode_base64_response(b64_result)
        if not success:
            return False, result
        image_bytes = result

        # Prepare output path
        if not output_name:
            name = os.path.splitext(os.path.basename(image_path))[0]
            output_name = f"{name}_segmented.png"
        output_path = os.path.join(settings.OUTPUT_DIR, output_name)

        # Save processed image
        return self._save_processed_image(image_bytes, output_path)

def main():
    """Example usage of SegmentationService"""
    service = SegmentationService()
    
    # Test configuration
    test_config = {
        "image_path": os.path.join(project_root, "input-images", "tt18.jpg"),
        "output_name": "tt18_segmented.png"
    }
    
    success, result = service.segment_image(
        image_path=test_config["image_path"],
        output_name=test_config["output_name"]
    )
    
    if success:
        logger.info(f"Image processing completed successfully: {result}")
    else:
        logger.error(f"Image processing failed: {result}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()