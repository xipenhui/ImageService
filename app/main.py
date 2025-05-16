# main.py
from fastapi import FastAPI
from app.api.routes import router as image_router

app = FastAPI()

app.include_router(image_router, prefix="/api")

@app.get("/hello")
def hello():
    return {"message": "Hello, world"}
