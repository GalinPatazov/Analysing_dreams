import time

from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.http import Http404
from .models import Dream, Favorite, AIAnalysisDailyUsage
from .ai_services import analyze_dream, generate_dream_image
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


DAILY_AI_ANALYSIS_LIMIT = 3


def _can_consume_ai_analysis(user) -> bool:
    # Admins have unlimited usage
    if user.is_staff or user.is_superuser:
        return True

    today = timezone.localdate()
    usage = AIAnalysisDailyUsage.objects.filter(user=user, date=today).first()
    if not usage:
        return True
    return usage.count < DAILY_AI_ANALYSIS_LIMIT


@transaction.atomic
def _consume_ai_analysis(user) -> bool:
    """
    Returns True if quota was consumed successfully, False if user is out of quota.
    Uses a row lock to avoid race conditions (double submits, parallel requests, etc.).
    """
    if user.is_staff or user.is_superuser:
        return True

    today = timezone.localdate()
    usage, _ = AIAnalysisDailyUsage.objects.select_for_update().get_or_create(
        user=user,
        date=today,
        defaults={"count": 0},
    )

    if usage.count >= DAILY_AI_ANALYSIS_LIMIT:
        return False

    usage.count += 1
    usage.save(update_fields=["count"])
    return True


# Create a new dream
class DreamCreateView(LoginRequiredMixin, CreateView):
    model = Dream
    fields = ['name', 'text']
    template_name = 'dreams_app/new_dream.html'
    success_url = reverse_lazy('dreams_app:my_dreams')

    def form_valid(self, form):
        dream = form.save(commit=False)
        dream.user = self.request.user

        # Enforce daily limit for non-admin users
        if not _consume_ai_analysis(self.request.user):
            messages.error(
                self.request,
                "Daily AI analysis limit reached (3/day). Please try again tomorrow."
            )
            dream.analysis_text = "Daily AI analysis limit reached. Please try again tomorrow."
            dream.image = None
            dream.save()
            return redirect(self.success_url)

        # 1. Generate analysis text
        dream.analysis_text = analyze_dream(dream.text)

        # 2. Generate image (bytes)
        image_bytes = generate_dream_image(dream.text)

        # 3. Save image properly
        if image_bytes:
            filename = f"dream_{self.request.user.id}_{int(time.time())}.png"
            dream.image.save(
                filename,
                ContentFile(image_bytes),
                save=False
            )

        dream.save()
        return redirect(self.success_url)

class DreamUpdateView(LoginRequiredMixin, UpdateView):
    model = Dream
    fields = ['name', 'text']
    template_name = 'dreams_app/dream_edit.html'

    def get_queryset(self):
        return Dream.objects.filter(user=self.request.user)

    def form_valid(self, form):
        dream = form.save(commit=False)

        # Check if text changed or if metadata is missing
        needs_regen = ('text' in form.changed_data) or (not dream.analysis_text) or (not dream.image)
        if needs_regen:
            # If we're going to hit the AI, enforce the daily limit
            if not _consume_ai_analysis(self.request.user):
                messages.error(
                    self.request,
                    "Daily AI analysis limit reached (3/day). Please try again tomorrow."
                )

                # If text changed, old analysis/image would no longer match; clear them.
                if 'text' in form.changed_data:
                    if dream.image:
                        dream.image.delete(save=False)
                    dream.image = None
                    dream.analysis_text = "Daily AI analysis limit reached. Please try again tomorrow."

                dream.save()
                return redirect('dreams_app:detail', pk=dream.pk)

            # 1. Regenerate Analysis
            dream.analysis_text = analyze_dream(dream.text)
            
            # 2. Regenerate Image
            image_bytes = generate_dream_image(dream.text)
            if image_bytes:
                # Delete old image file if it exists to avoid clutter
                if dream.image:
                    dream.image.delete(save=False)
                
                filename = f"dream_{self.request.user.id}_{int(time.time())}.png"
                dream.image.save(filename, ContentFile(image_bytes), save=False)

        dream.save()
        return redirect('dreams_app:detail', pk=dream.pk)

class DreamDeleteView(LoginRequiredMixin, DeleteView):
    model = Dream
    template_name = 'dreams_app/dream_confirm_delete.html'
    success_url = reverse_lazy('dreams_app:my_dreams')

    def get_queryset(self):
        return Dream.objects.filter(user=self.request.user)

# List only current user's dreams
class DreamListView(LoginRequiredMixin, ListView):
    model = Dream
    template_name = 'dreams_app/my_dreams.html'
    context_object_name = 'dreams'

    def get_queryset(self):
        return Dream.objects.filter(user=self.request.user).order_by('-created_at')

# Dream detail
def dream_detail(request, pk):
    dream = get_object_or_404(Dream, pk=pk)
    if dream.user != request.user:
        raise Http404("This dream does not exist")
    
    is_favorite = Favorite.objects.filter(user=request.user, dream=dream).exists()
    
    return render(request, 'dreams_app/dream_detail.html', {
        'dream': dream,
        'is_favorite': is_favorite
    })

# @require_POST
@login_required
def toggle_favorite(request, pk):
    dream = get_object_or_404(Dream, pk=pk, user=request.user)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        dream=dream
    )

    if not created:
        favorite.delete()

    return redirect('dreams_app:detail', pk=pk)

class FavoriteListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'dreams_app/favorites.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return (
            Favorite.objects
            .filter(user=self.request.user)
            .select_related('dream')
            .order_by('-created_at')
        )