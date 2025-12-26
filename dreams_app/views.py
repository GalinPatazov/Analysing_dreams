from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import Dream
from .forms import DreamForm
from django.views.generic import ListView


class DreamCreateView(LoginRequiredMixin, CreateView):
    model = Dream
    form_class = DreamForm
    template_name = 'dreams_app/new_dream.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        dream = form.save(commit=False)
        dream.user = self.request.user
        dream.analysis_text = "AI analysis will be here (coming soon)"
        dream.image = "https://via.placeholder.com/400"
        dream.save()
        return super().form_valid(form)


class DreamListView(LoginRequiredMixin, ListView):
    model = Dream
    template_name = 'dreams_app/my_dreams.html'
    context_object_name = 'dreams'
    ordering = ['-created_at']

    def get_queryset(self):
        return Dream.objects.filter(user=self.request.user)