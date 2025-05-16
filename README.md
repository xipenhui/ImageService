# Image Service

一个用于图像处理的 Python 服务，提供图像分割和背景处理功能。

## 功能特点

- 图像分割（通过 API）
- 背景处理（支持自定义背景色和宽高比）
- 图像锐化处理

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/你的用户名/ImageService.git
cd ImageService
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -e .
```

启动服务
```
 uvicorn app.main:app --port 51060                                     
```
## 使用方法

### 图像分割
```python
from app.utils.segment import SegmentationService

service = SegmentationService()
success, result = service.segment_image(
    image_path="path/to/image.jpg",
    output_name="output.png"
)
```

### 背景处理
```python
from app.utils.background import BackgroundProcessor

processor = BackgroundProcessor()
processor.add_background(
    image_path="path/to/image.png",
    background_color=(255, 255, 255),
    output_path="output.jpg",
    target_aspect_ratio=(9, 16)
)
```

