from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[],
)