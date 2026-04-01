from django.contrib.auth import login
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
        # TODO integrate into user settings
        if match_found:
            return redirect(f'/dashboard/?status=matched&person_id={matched_person.id}')
        else:
            return redirect('/dashboard/?status=no_match')

    else:
        return render(request, 'activation_invalid.html', {'error': 'Invalid link'})

class CustomPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('auth:password_reset_done')