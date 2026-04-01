import re

from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from accounts.forms import CustomUserCreationForm
from app import settings
from swimpro.models import Person


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            send_verification_email(request, user)

            return render(request, 'registration/verification_sent.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def account_settings(request):
    """
    Handles updating username, email (with confirmation), and password.
    """
    if request.method == 'POST':
        # 1. Extract Data
        new_username = request.POST.get('username', '').strip()
        new_email = request.POST.get('email', '').strip().lower()
        email_confirm = request.POST.get('email_confirm', '').strip().lower()
        new_password1 = request.POST.get('new_password1', '')
        new_password2 = request.POST.get('new_password2', '')

        # 2. Validation Flags
        is_valid = True

        # --- Username Validation ---
        if new_username and new_username != request.user.username:
            if len(new_username) < 3:
                messages.error(request, "Username must be at least 3 characters long.")
                is_valid = False
            elif User.objects.filter(username=new_username).exists():
                messages.error(request, "This username is already taken.")
                is_valid = False
            # Optional: Regex for valid username characters
            elif not re.match(r'^[\w.@+-]+$', new_username):
                messages.error(request, "Username can only contain letters, numbers, and @/./+/-/_ characters.")
                is_valid = False

        # --- Email Validation & Confirmation ---
        if new_email and new_email != request.user.email:
            if new_email != email_confirm:
                messages.error(request, "The new email and confirmation email do not match.")
                is_valid = False
            elif User.objects.filter(email=new_email).exists():
                messages.error(request, "An account with this email already exists.")
                is_valid = False
            else:
                # Basic email format check (Django forms usually handle this better, but good for raw POST)
                if '@' not in new_email or '.' not in new_email:
                    messages.error(request, "Please enter a valid email address.")
                    is_valid = False

        # --- Password Validation ---
        if new_password1 or new_password2:
            if not new_password1 or not new_password2:
                messages.error(request, "Both password fields are required to change the password.")
                is_valid = False
            elif new_password1 != new_password2:
                messages.error(request, "Passwords do not match.")
                is_valid = False
            elif len(new_password1) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                is_valid = False
            # Optional: Add complexity checks here (digits, uppercase, etc.)

        # 3. Process Changes if Valid
        if is_valid:
            try:
                # Update Username
                if new_username and new_username != request.user.username:
                    request.user.username = new_username

                # Update Email
                if new_email and new_email != request.user.email:
                    # TODO person handling + validation
                    request.user.email = new_email

                # Update Password
                if new_password1:
                    request.user.set_password(new_password1)
                    # Keep user logged in after password change
                    update_session_auth_hash(request, request.user)

                request.user.save()
                messages.success(request, "Your account settings have been updated successfully.")
                return redirect('settings')  # Redirect to clear POST data

            except Exception as e:
                messages.error(request, f"An error occurred while updating your account: {str(e)}")

    # 4. Render Template
    # We pass the current user's data to pre-fill the form fields
    context = {
        'form': {
            'username': request.user.username,
            'email': request.user.email,
            # Password fields are empty by default for security
            'new_password1': '',
            'new_password2': '',
        },
        # You can also pass the raw user object if your template prefers accessing user.username directly
        'user': request.user
    }

    return render(request, 'registration/settings.html', context)

def send_verification_email(request, user):
    """Generates token and sends email"""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # Construct your custom link
    url_path = reverse('auth:activate', kwargs={'uidb64': uid, 'token': token})
    link = f"{request.scheme}://{request.get_host()}{url_path}"

    send_mail(
        subject="Verify your email",
        message=f"Please click the link to verify: {link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
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
        match_found = False
        matched_person = None

        try:
            # Attempt to find a Person with this exact email
            matched_person = Person.objects.get(email=user.e_mail)
            match_found = True

            # Optional: Link the user to the person if you have a UserProfile
            # profile, created = UserProfile.objects.get_or_create(user=user)
            # profile.person = matched_person
            # profile.save()

            # Or simply log it / set a flag in session for the frontend
            request.session['person_match_status'] = 'found'
            request.session['person_id'] = matched_person.id

        except Person.DoesNotExist:
            match_found = False
            request.session['person_match_status'] = 'not_found'

        # 3. Log the user in automatically
        login(request, user)

        # 4. Redirect with status
        # You can pass the status as a query param or rely on the session
        # TODO intigrate status message
        if match_found:
            return redirect('settings')
        else:
            return redirect('settings')

    else:
        return render(request, 'registration/activation_invalid.html', {'error': 'Invalid link'})

class CustomPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('auth:password_reset_done')