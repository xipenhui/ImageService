from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from app.services.image_service import ImageService
from app.core.config import settings
import random

router = APIRouter()
image_service = ImageService()

class Base64Request(BaseModel):
    image_base64: str
    bg_color: List[int] = Field(default_factory=list)
    aspect_ratio: List[int] = Field(default=[9, 16])

class PathRequest(BaseModel):
    input_image: str
    bg_color: List[int] = Field(default_factory=list)
    output_image: Optional[str] = None
    aspect_ratio: List[int] = Field(default=[9, 16])

@router.get("/hello")
async def say_hello():
    return {"message": "Hello from FastAPI"}

async def process_image(
    request: Base64Request | PathRequest,
    process_type: Literal["base64", "path"],
    force_random_bg: bool = False
):
    try:
        if force_random_bg and request.bg_color:
            raise HTTPException(
                status_code=400,
                detail="Cannot set bg_color when using random background"
            )
        print(f"settings.RANDOM_BG_ENABLE: {settings.RANDOM_BG_ENABLE}")
        print(f"force_random_bg: {force_random_bg}")
        if (settings.RANDOM_BG_ENABLE or force_random_bg):
            bg_color = random_bg_color(request.bg_color)
        else:
            bg_color = request.bg_color
        print(f"bg_color: {bg_color}, ratio: {request.aspect_ratio}, process_type: {process_type}")
        if process_type == "base64":
            result = await image_service.process_base64_image(
                image_base64=request.image_base64,
                bg_color=bg_color,
                aspect_ratio=request.aspect_ratio
            )
        else:
            result = await image_service.process_path_image(
                input_image=request.input_image,
                bg_color=bg_color,
                output_image=request.output_image,
                aspect_ratio=request.aspect_ratio
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process/base64")
async def process_base64(request: Base64Request):
    return await process_image(request, "base64")

@router.post("/process/path")
async def process_path(request: PathRequest):
    return await process_image(request, "path")

@router.post("/process/base64/randombg")
async def process_base64_random(request: Base64Request):
    return await process_image(request, "base64", force_random_bg=True)

@router.post("/process/path/randombg")
async def process_path_random(request: PathRequest):
    return await process_image(request, "path", force_random_bg=True)

def random_bg_color(bg_color: List[int]) -> List[int]:
    bg_color = random.choice(settings.BG_COLOR)
    print(f"Using random bg_color: {bg_color}")
    return bg_color