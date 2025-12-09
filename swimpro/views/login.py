from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView as BaseLoginView
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import FormView

from swimpro.forms import RegisterForm, PasswordResetRequestForm
from swimpro.models import Person


class LoginView(BaseLoginView):
    template_name = "login.html"
    redirect_authenticated_user = True
    success_url = "/"


class RegisterView(FormView):
    template_name = "register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save()
        Person.objects.filter(user=user).update(is_approved=False)

        # TODO setup for SMTP server for testing
        # email to admins
        # send_mail(
        #     "New user awaiting approval",
        #     f"User {user.username} is awaiting approval.",
        #     "no-reply@example.com",
        #     ["admin@example.com"],
        # )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "title": "Create Account",
            "heading": "Register",
            "button_label": "Register",
            "mode": "register",
        })
        return ctx

class PasswordResetRequestView(FormView):
    template_name = "register.html"
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return super().form_valid(form)  # silent fail for security

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = self.request.build_absolute_uri(
            reverse_lazy("password_reset_verify", kwargs={"uidb64": uid, "token": token})
        )

        send_mail(
            "Password Reset",
            f"Click to reset your password: {reset_link}",
            "no-reply@example.com",
            [email],
        )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "title": "Reset Password",
            "heading": "Password Reset",
            "button_label": "Send Reset Email",
            "mode": "reset",
        })
        return ctx

def password_reset_verify(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        return HttpResponse("Invalid link.")

    if not default_token_generator.check_token(user, token):
        return HttpResponse("Invalid or expired token.")

    if request.method == "POST":
        pw1 = request.POST.get("password1")
        pw2 = request.POST.get("password2")

        if pw1 != pw2:
            return render(request, "password_reset_form.html", {"error": "Passwords do not match."})

        user.set_password(pw1)
        user.save()
        return redirect("login")

    return render(request, "password_reset_form.html")


@staff_member_required
def approve_users(request):
    pending = User.objects.filter(is_active=False)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user = User.objects.get(pk=user_id)
        user.is_active = True
        user.userprofile.is_approved = True
        user.save()
        user.userprofile.save()

        # notify user
        send_mail(
            "Your account is approved",
            "Your account has been activated. You can now log in.",
            "no-reply@example.com",
            [user.email],
        )
        return redirect("approve_users")