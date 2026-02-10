from fastapi import APIRouter, Depends, status

router = APIRouter(
    prefix="/ask",
    tags=["ask"],
    dependencies=[],
)

@router.get("/", status_code=status.HTTP_200_OK)
async def ask_question():
    return {"message": "Question received"}

@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm_question():
    return {"message": "Question confirmed"}
