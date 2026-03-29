from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class LoginView(BaseLoginView):
    template_name = "login.html"
    redirect_authenticated_user = True
    success_url = "/"
