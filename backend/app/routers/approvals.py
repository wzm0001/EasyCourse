from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.common import APIResponse, PageResponse
from app.schemas.user import ApprovalInfo, ApprovalAction
from app.repositories.user import ApprovalRepository
from app.middleware.auth import require_super_admin, get_current_user_dependency

router = APIRouter(prefix="/approvals", tags=["审批管理"])


@router.get("", response_model=APIResponse[PageResponse[ApprovalInfo]])
async def get_approvals(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    approval_repo = ApprovalRepository(db)
    if current_user.role == UserRole.SUPER_ADMIN:
        records, total = await approval_repo.get_all(page=page, page_size=page_size)
    else:
        if not current_user.school_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
        records, total = await approval_repo.get_by_school(current_user.school_id, page=page, page_size=page_size)
    items = [
        ApprovalInfo(
            id=r.id,
            type=r.type,
            requester_id=r.requester_id,
            school_id=r.school_id,
            status=r.status,
            request_data=r.request_data,
            reject_reason=r.reject_reason,
            reviewer_id=r.reviewer_id,
            created_at=r.created_at,
        )
        for r in records
    ]
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.get("/pending", response_model=APIResponse[PageResponse[ApprovalInfo]])
async def get_pending_approvals(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    approval_repo = ApprovalRepository(db)
    records, total = await approval_repo.get_pending(page=page, page_size=page_size)
    items = [
        ApprovalInfo(
            id=r.id,
            type=r.type,
            requester_id=r.requester_id,
            school_id=r.school_id,
            status=r.status,
            request_data=r.request_data,
            reject_reason=r.reject_reason,
            reviewer_id=r.reviewer_id,
            created_at=r.created_at,
        )
        for r in records
    ]
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.post("/{approval_id}/approve", response_model=APIResponse)
async def approve_approval(
    approval_id: str,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.user import ApprovalRepository
    from app.services.user import approve_school, approve_data_change
    from app.services.notification import send_approval_result

    approval_repo = ApprovalRepository(db)
    record = await approval_repo.get_by_id(approval_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批记录不存在")
    if record.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该审批已经处理")

    if record.type == "school_registration":
        await approve_school(record.school_id, current_user.id, db)
        approval_repo = ApprovalRepository(db)
        await approval_repo.update(approval_id, {"status": "approved", "reviewer_id": current_user.id})
    else:
        await approve_data_change(approval_id, current_user.id, db)

    await send_approval_result(approval_id, True, None, db)
    return APIResponse.success(message="审批已通过")


@router.post("/{approval_id}/reject", response_model=APIResponse)
async def reject_approval(
    approval_id: str,
    request: ApprovalAction,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.user import ApprovalRepository
    from app.services.user import reject_school, reject_data_change
    from app.services.notification import send_approval_result

    approval_repo = ApprovalRepository(db)
    record = await approval_repo.get_by_id(approval_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批记录不存在")
    if record.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该审批已经处理")

    if record.type == "school_registration":
        await reject_school(record.school_id, current_user.id, request.reject_reason or "", db)
        approval_repo = ApprovalRepository(db)
        await approval_repo.update(approval_id, {"status": "rejected", "reviewer_id": current_user.id, "reject_reason": request.reject_reason or ""})
    else:
        await reject_data_change(approval_id, current_user.id, request.reject_reason or "", db)

    await send_approval_result(approval_id, False, request.reject_reason, db)
    return APIResponse.success(message="审批已拒绝")
