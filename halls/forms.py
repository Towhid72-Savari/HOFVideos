from django import forms
from halls import models


class VideoForm(forms.ModelForm):
    class Meta:
        model = models.Video
        fields = ['url']
        labels = {'url': 'Youtube Url'}


class SearchFrom(forms.Form):
    search_term = forms.CharField(max_length=255, label='Search for videos')