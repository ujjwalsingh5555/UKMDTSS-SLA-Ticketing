# ticketingapp/helpers.py
from loginApp.models import Registeruse, RolePermissionMapping
def get_logged_in_user(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return Registeruse.objects.filter(
        id=user_id,
        is_active=True
    ).select_related("role").first()
    
def user_has_permission(request, permission_code):
    user = get_logged_in_user(request)
    if not user:
        return False
    return has_permission(user,permission_code)


def has_permission(user, permission_code):
    if not user:
        return False
    if not user.role:
        return False
    if not user.role.is_active:
        return False
    return RolePermissionMapping.objects.filter(
        role=user.role,
        permission__code=permission_code,
        permission__is_active=True,
        is_active=True).exists()
