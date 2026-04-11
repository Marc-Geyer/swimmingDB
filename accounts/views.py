import re

from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from accounts.forms import CustomUserCreationForm, EmailChangeForm
from accounts.models import SwimProUser
from app import settings
from swimpro.models import Person

from django.contrib.auth import get_user_model

from swimpro.models.through_models import UserPerson

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            send_verification_email(request, user, user.email ,purpose='activate_account')

            return render(request, 'registration/verification_sent.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def account_settings(request):
    """
    Read-only account overview with links to change pages.
    """
    context = {
        'user': request.user,
        'pending_email': getattr(request.user, 'pending_email', None),
        'email_verified_pending': getattr(request.user, 'email_verification_pending', False),
    }
    return render(request, 'registration/account_settings.html', context)

@login_required
def username_change(request):
    """
    Change username (no verification needed).
    """
    if request.method == 'POST':
        new_username = request.POST.get('username', '').strip()

        # Validation
        if not new_username:
            messages.error(request, "Please enter a new username.")
            return redirect('auth:username_change')

        if len(new_username) < 3:
            messages.error(request, "Username must be at least 3 characters.")
            return redirect('auth:username_change')

        if new_username == request.user.username:
            messages.warning(request, "This is your current username.")
            return redirect('auth:username_change')

        if User.objects.filter(username=new_username).exists():
            messages.error(request, "This username is already taken.")
            return redirect('auth:username_change')

        if not re.match(r'^[\w.@+-]+$', new_username):
            messages.error(request, "Username can only contain letters, numbers, and @/./+/-/_ characters.")
            return redirect('auth:username_change')

        # Apply change
        request.user.username = new_username
        request.user.save()

        messages.success(request, "Your username has been updated.")
        return redirect('auth:settings')

    return render(request, 'registration/username_change.html', {'user': request.user})


@login_required
def email_change(request):
    """
    Handle email change with verification flow.
    """
    if request.method == 'POST':
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['email']

            # Additional Security Checks
            if new_email == request.user.email:
                messages.warning(request, "This is your current email address.")
                return redirect('auth:email_change')

            if User.objects.filter(email=new_email).exists():
                messages.error(request, "An account with this email already exists.")
                return redirect('auth:email_change')

            # Store pending email
            request.user.pending_email = new_email
            request.user.email_verification_pending = True
            request.user.save()

            # Send Verification Email
            send_verification_email(request, request.user, new_email, purpose='email_change')

            messages.success(request, f"Verification email sent to {new_email}. Please check your inbox.")
            return redirect('auth:email_change_done')
    else:
        form = EmailChangeForm()

    # Render the template with the form instance
    return render(request, 'registration/email_change.html', {
        'form': form,
        'current_email': request.user.email
    })

@login_required
def email_change_confirmation(request):
    """
    Page shown after submitting new email, waiting for verification.
    """
    if not getattr(request.user, 'email_verification_pending', False):
        return redirect('auth:settings')

    return render(request, 'registration/email_change_confirmation.html', {
        'pending_email': request.user.pending_email
    })


def email_change_verify(request, uidb64, token):
    """
    Verify email change token and finalize the change.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return render(request, 'registration/verification_invalid.html', {'error': 'Invalid link'})

    if not default_token_generator.check_token(user, token):
        return render(request, 'registration/verification_invalid.html', {'error': 'Expired or invalid token'})

    if not getattr(user, 'email_verification_pending', False):
        messages.warning(request, "No pending email change found.")
        return redirect('auth:settings')

    # Finalize email change
    user.email = user.pending_email
    user.pending_email = None
    user.email_verification_pending = False
    user.save()

    messages.success(request, "Your email has been successfully updated.")
    return redirect('auth:settings')

def send_verification_email(request, user, new_email, purpose='email_change'):
    """
    Generate token and send verification email.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    if purpose == 'email_change':
        url_path = reverse('auth:email_change_verify', kwargs={'uidb64': uid, 'token': token})
        subject = "Verify Your New Email Address"
        message = f"""
Hello,

You requested to change your email address to {new_email}.

Please click the link below to verify:
{request.scheme}://{request.get_host()}{url_path}

If you did not request this change, please ignore this email.

Thank you,
Your SwimPro Team
"""
    else:
        # For account activation
        url_path = reverse('auth:activate', kwargs={'uidb64': uid, 'token': token})
        subject = "Activate Your Account"
        message = f"""
Hello,

Welcome to SwimPro! Please click the link below to activate your account:
{request.scheme}://{request.get_host()}{url_path}

Thank you,
Your SwimPro Team
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[new_email if purpose == 'email_change' else user.email],
        fail_silently=False,
    )

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # 1. Activate the user
        user.is_active = True
        user.save()

        # 2. Perform the Person Match Check
        # Attempt to find a Persons with this exact email
        matched_persons = Person.objects.filter(e_mail=user.email)
        if matched_persons:
            for person in matched_persons:
                relation, _ = UserPerson.objects.get_or_create(user=user, person=person)

                if relation.person.get_age() < 14:
                    relation.relation = UserPerson.Relation.CHILD
                relation.save()

        # 3. Log the user in automatically
        login(request, user)

        # 4. Redirect with status
        messages.success(request, "You have successfully activated your account.")
        if matched_persons:
            messages.success(request, "You where successfully matched with a Person on record")
            return redirect('auth:settings')
        else:
            messages.warning(request, "You have not matched with a Person on record")
            return redirect('auth:settings')

    else:
        return render(request, 'registration/verification_invalid.html', {'error': 'Invalid link'})

class CustomPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('auth:password_reset_done')

class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('auth:password_change_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('auth:password_reset_complete')  # TODO: refrence her to settings (maybe get message to display)