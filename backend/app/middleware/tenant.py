from typing import Optional

from app.models.user import User, UserRole


class TenantFilter:
    def __init__(self, school_id: Optional[str]):
        self.school_id = school_id

    def apply(self, query, model):
        if self.school_id is not None:
            if hasattr(model, "school_id"):
                query = query.where(model.school_id == self.school_id)
        return query


def get_tenant_filter(current_user: User) -> TenantFilter:
    if current_user.role == UserRole.SUPER_ADMIN:
        return TenantFilter(school_id=None)
    return TenantFilter(school_id=current_user.school_id)
