import time

from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.http import Http404
from .models import Dream, Favorite
from .ai_services import analyze_dream, generate_dream_image
from django.core.files.base import ContentFile

# Create a new dream
class DreamCreateView(LoginRequiredMixin, CreateView):
    model = Dream
    fields = ['name', 'text']
    template_name = 'dreams_app/new_dream.html'
    success_url = reverse_lazy('dreams_app:my_dreams')

    def form_valid(self, form):
        dream = form.save(commit=False)
        dream.user = self.request.user

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
        if 'text' in form.changed_data or not dream.analysis_text or not dream.image:
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

def toggle_favorite(request, pk):
    dream = get_object_or_404(Dream, pk=pk)

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