from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if a user with this email already exists (active or inactive)
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email address is already registered.")
        return email


class EmailChangeForm(forms.Form):
    email = forms.EmailField(
        label="New Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new email',
            'autofocus': True
        }),
        help_text="Please enter your new email address."
    )
    email_confirm = forms.EmailField(
        label="Confirm New Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repeat new email'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        email_confirm = cleaned_data.get("email_confirm")

        if email and email_confirm and email != email_confirm:
            raise forms.ValidationError("The email addresses do not match.")

        return cleaned_data