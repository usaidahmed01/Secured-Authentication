from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models import User
from app.schemas import UserRegistrationResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserRegistrationResponse,
)
async def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user