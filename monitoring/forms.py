from .models import Url
from django.forms import ModelForm, TextInput


class UrlForm(ModelForm):
    class Meta:
        model = Url
        fields = ['url']
        widgets = {
            'url': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Input urls separated with space'
            }
                             )
                   }
