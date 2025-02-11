# app/api/endpoints/root.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["Root"])
async def read_root():
    return {"message": "Train Delay API is running!"}