from django import forms
from .models import Dream

class DreamForm(forms.ModelForm):
    class Meta:
        model = Dream
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Describe your dream...'
            })
        }
