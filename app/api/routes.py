from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.image_service import ImageService

router = APIRouter()
image_service = ImageService()

class Base64Request(BaseModel):
    image_base64: str
    bg_color: Optional[List[int]] = [255, 255, 255]
    aspect_ratio: Optional[List[int]] = [9, 16]

class PathRequest(BaseModel):
    input_image: str
    bg_color: Optional[List[int]] = [255, 255, 255]
    output_image: Optional[str] = None

@router.get("/hello")
async def say_hello():
    return {"message": "Hello from FastAPI"}

@router.post("/process/base64")
async def process_base64(request: Base64Request):
    try:
        result = await image_service.process_base64_image(
            image_base64=request.image_base64,
            bg_color=request.bg_color,
            aspect_ratio=request.aspect_ratio
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process/path")
async def process_path(request: PathRequest):
    try:
        print(f"request: {request}")
        result = await image_service.process_path_image(
            input_image=request.input_image,
            bg_color=request.bg_color,
            output_image=request.output_image
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
