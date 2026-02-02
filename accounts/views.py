from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

from dreams_app.models import Dream, Favorite
from .forms import CustomUserCreationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # <-- changed

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # <-- changed
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # <-- changed

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')  # <-- changed
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')


def _role_for_dream_count(dream_count: int) -> str:
    if dream_count >= 50:
        return _("Lucid Legend")
    if dream_count >= 20:
        return _("Dream Weaver")
    if dream_count >= 5:
        return _("Night Explorer")
    if dream_count >= 1:
        return _("New Dreamer")
    return _("Just Arrived")


@login_required
def profile_view(request):
    dreams = Dream.objects.filter(user=request.user)

    dream_count = dreams.count()
    favorites_count = Favorite.objects.filter(user=request.user).count()

    days_active = (
        dreams
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .distinct()
        .count()
    )

    role = _role_for_dream_count(dream_count)

    return render(request, "accounts/profile.html", {
        "dream_count": dream_count,
        "favorites_count": favorites_count,
        "days_active": days_active,
        "role": role,
    })