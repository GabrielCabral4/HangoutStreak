from django import forms
from .models import Event, EventPhoto
from django.utils import timezone

class EventForm(forms.ModelForm):
    date = forms.DateTimeField(
        label='Data e Hora',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'max_participants', 'image', 'is_private']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Digite o título do evento'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva o evento'})
        self.fields['location'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Digite o local do evento'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['max_participants'].widget.attrs.update({'class': 'form-control', 'min': 0})
        self.fields['is_private'].widget.attrs.update({'class': 'form-check-input'})
        
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now():
            raise forms.ValidationError('A data do evento não pode ser no passado.')
        return date 

class EventPhotoForm(forms.ModelForm):
    class Meta:
        model = EventPhoto
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Adicione uma legenda (opcional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['caption'].required = False 