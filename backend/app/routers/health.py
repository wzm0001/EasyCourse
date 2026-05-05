from fastapi import APIRouter

from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/health", response_model=APIResponse)
async def health_check():
    return APIResponse.success(data={"status": "healthy"})
