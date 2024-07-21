from django import forms
from .models import Room

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_name', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-control'})