# main.py
from fastapi import FastAPI
from app.api.routes import router as image_router
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import applications

# 猴子补丁替换 CDN 链接
def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.6.2/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.6.2/swagger-ui.min.css"
    )

applications.get_swagger_ui_html = swagger_monkey_patch

app = FastAPI()

app.include_router(image_router, prefix="/api")

@app.get("/hello")
def hello():
    return {"message": "Hello, world"}
