from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.http import Http404
from .models import Dream
from .ai_services import analyze_dream, generate_dream_image

# Create a new dream
class DreamCreateView(LoginRequiredMixin, CreateView):
    model = Dream
    fields = ['name', 'text']  # name + text
    template_name = 'dreams_app/new_dream.html'
    success_url = reverse_lazy('dreams_app:my_dreams')

    def form_valid(self, form):
        dream = form.save(commit=False)
        dream.user = self.request.user
        dream.analysis_text = analyze_dream(dream.text)
        dream.image = generate_dream_image(dream.text)
        dream.save()
        return super().form_valid(form)

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
    return render(request, 'dreams_app/dream_detail.html', {'dream': dream})