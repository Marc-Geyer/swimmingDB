from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    PUBLIC_PATHS = ["/login/", "/register/", "/public/"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.lower()
        if any(keyword in path for keyword in self.PUBLIC_PATHS):
            return self.get_response(request)

        user = getattr(request, "user", None)
        if not user:
            return redirect("login")
        if not user.is_authenticated:
            return redirect("login")

        return self.get_response(request)


class AttachPersonMiddleware:
    """
    Adds a `person` attribute to every request.
    If user is logged in, request.person = user's Person object.
    If not logged in, request.person = None
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated and hasattr(user, "person"):
            request.person = user.person
        else:
            request.person = None

        response = self.get_response(request)
        return response