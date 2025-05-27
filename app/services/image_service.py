import os
import base64
import tempfile
from PIL import Image
from io import BytesIO
from app.core.config import settings
import random
import logging

logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Import custom modules
from app.utils.segment import SegmentationService
from app.utils.background import BackgroundProcessor

class ImageService:
    def __init__(self):
        self.OUTPUT_DIR = settings.OUTPUT_DIR
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        self.segmentation_service = SegmentationService()
        self.background_processor = BackgroundProcessor()
        self.logger = logging.getLogger(__name__)

    async def _process_image(self, image_path: str, bg_color: list, aspect_ratio: list, output_name: str = None) -> dict:
        """Common image processing logic for both base64 and path inputs"""
        try:
            # 1. Call segmentation service
            temp_output_name = f"segmented_{os.path.basename(image_path)}"
            self.logger.info(f"Processing image: {image_path}")
            self.logger.info(f"Target aspect ratio: {aspect_ratio}")
            print(f"target aspect ratio: {aspect_ratio}")
            success, segmented_path = self.segmentation_service.segment_image(image_path, temp_output_name)
            
            if not success:
                raise Exception(f"Segmentation failed: {segmented_path}")
            
            # 2. Generate output filename if not provided
            if not output_name:
                name, _ = os.path.splitext(os.path.basename(image_path))
                aspect_str = f"_{aspect_ratio[0]}_{aspect_ratio[1]}"
                output_name = f"{name}_processed{aspect_str}.jpg"
            
            final_output_path = os.path.join(self.OUTPUT_DIR, output_name)
            self.logger.info(f"Final output path: {final_output_path}")
            
            # 3. Add background and adjust size
            self.logger.info(f"Adding background with color: {bg_color}")
            self.background_processor.add_background(
                image_path=segmented_path,
                background_color=tuple(bg_color),
                output_path=final_output_path,
                target_aspect_ratio=aspect_ratio
            )
            
            return {
                "segmented_path": segmented_path,
                "final_path": final_output_path
            }
            
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            raise e

    async def process_base64_image(self, image_base64: str, bg_color: list = [], aspect_ratio: list = [9, 16]):
        try:
            # 1. Process base64 string
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            image_bytes = base64.b64decode(image_base64)
            
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_input_path = temp_file.name
                temp_file.write(image_bytes)
            
            print(f"base 64 aspect ratio: {aspect_ratio}")
            # 2. Process image using common logic
            result = await self._process_image(
                image_path=temp_input_path,
                bg_color=bg_color,
                aspect_ratio=aspect_ratio,
                output_name=f"processed_{os.path.basename(temp_input_path)}"
            )
            
            # 3. Convert processed image to base64
            with open(result["final_path"], "rb") as f:
                processed_bytes = f.read()
            
            output_b64 = base64.b64encode(processed_bytes).decode('utf-8')
            
            # 4. Cleanup
            os.unlink(temp_input_path)
            
            return {
                **result,
                "result_base64": f"data:image/png;base64,{output_b64}",
                "aspect_ratio": aspect_ratio
            }
            
        except Exception as e:
            if 'temp_input_path' in locals() and os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            raise e

    async def process_path_image(self, input_image: str, bg_color: list = [], output_image: str = None, aspect_ratio: list = [9, 16]):
        if not os.path.exists(input_image):
            raise Exception(f"Invalid path: {input_image}")
            
        self.logger.info(f"Processing path image: {input_image}")
        self.logger.info(f"Output image: {output_image}")
        self.logger.info(f"Background color: {bg_color}")
        self.logger.info(f"Aspect ratio: {aspect_ratio}")
        
        return await self._process_image(
            image_path=input_image,
            bg_color=bg_color,
            aspect_ratio=aspect_ratio,
            output_name=output_image
        )