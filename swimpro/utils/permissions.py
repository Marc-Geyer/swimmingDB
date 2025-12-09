import functools
from functools import wraps

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden


def require_privilege(level):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user

            # 1. User must be logged in
            if not user.is_authenticated:
                raise PermissionDenied("Not logged in.")

            # 2. Ensure the Person object exists
            if not hasattr(user, "person"):
                raise PermissionDenied("No Person profile linked to this user.")

            # 3. Check privilege level
            if user.person.privilege_level < level:
                return HttpResponseForbidden("You do not have permission to access this.")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator