from django.contrib.auth.views import PasswordResetView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from accounts.forms import CustomUserCreationForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('auth:password_reset_done')