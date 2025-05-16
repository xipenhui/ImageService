
import os
import base64
import tempfile
from PIL import Image
from io import BytesIO

# Import custom modules
from app.utils.segment import segment_image
from app.utils.background import add_background

class ImageService:
    def __init__(self):
        self.OUTPUT_DIR = "output"
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

    async def process_base64_image(self, image_base64: str, bg_color: list = [255, 255, 255], aspect_ratio: list = [9, 16]):
        try:
            # 1. Process base64 string
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            image_bytes = base64.b64decode(image_base64)
            
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_input_path = temp_file.name
                temp_file.write(image_bytes)
            
            # 2. Call segmentation service
            temp_output_name = f"temp_segmented_{os.path.basename(temp_input_path)}"
            success, segmented_path = segment_image(temp_input_path, temp_output_name)
            
            if not success:
                os.unlink(temp_input_path)
                raise Exception(f"Segmentation failed: {segmented_path}")
            
            # 3. Add background and adjust size
            target_aspect_ratio = tuple(aspect_ratio) if aspect_ratio else None
            final_output_path = os.path.join(self.OUTPUT_DIR, f"processed_{os.path.basename(temp_output_name)}")
            
            add_background(
                image_path=segmented_path,
                background_color=tuple(bg_color),
                output_path=final_output_path,
                target_aspect_ratio=target_aspect_ratio
            )
            
            # 4. Convert processed image to base64
            with open(final_output_path, "rb") as f:
                processed_bytes = f.read()
            
            output_b64 = base64.b64encode(processed_bytes).decode('utf-8')
            
            # 5. Cleanup
            os.unlink(temp_input_path)
            
            return {
                "result_base64": f"data:image/png;base64,{output_b64}",
                "segmented_path": segmented_path,
                "final_path": final_output_path
            }
            
        except Exception as e:
            if 'temp_input_path' in locals() and os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            raise e

    async def process_path_image(self, image_path: str, bg_color: list = [255, 255, 255], output_filename: str = None):
        if not os.path.exists(image_path):
            raise Exception(f"Invalid path: {image_path}")

        try:
            # 1. Call segmentation service
            temp_output_name = f"segmented_{os.path.basename(image_path)}"
            success, segmented_path = segment_image(image_path, temp_output_name)
            
            if not success:
                raise Exception(f"Segmentation failed: {segmented_path}")
            
            # 2. Add background and adjust size
            target_aspect_ratio = [9, 16]
            
            if not output_filename:
                name, _ = os.path.splitext(os.path.basename(image_path))
                aspect_str = f"_9_16"
                output_filename = f"{name}_processed{aspect_str}.jpg"
            
            final_output_path = os.path.join(self.OUTPUT_DIR, output_filename)
            
            add_background(
                image_path=segmented_path,
                background_color=tuple(bg_color),
                output_path=final_output_path,
                target_aspect_ratio=target_aspect_ratio
            )
            
            return {
                "segmented_path": segmented_path,
                "final_path": final_output_path
            }
            
        except Exception as e:
            raise e