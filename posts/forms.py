from django import forms
import requests
from django.core.exceptions import ValidationError
from posts.models import PostModel, MusicModel, HashtagModel, CommentModel


class PostModelForm(forms.ModelForm):
    latitude = forms.CharField(widget=forms.HiddenInput(), required=False)
    longitude = forms.CharField(widget=forms.HiddenInput(), required=False)
    location_name = forms.CharField(max_length=255, required=False)

    hashtags = forms.CharField(required=False)
    music = forms.ModelMultipleChoiceField(queryset=MusicModel.objects.all(), required=False)

    class Meta:
        model = PostModel
        fields = ['caption', 'post_type', 'contentUrl', 'location_name', 'latitude', 'longitude']

    def clean(self):
        cleaned = super().clean()
        name = cleaned.get('location_name')
        lat = cleaned.get('latitude')
        lon = cleaned.get('longitude')

        if name and (not lat or not lon):
            try:
                params = {
                    'q': name,
                    'format': 'jsonv2',
                    'limit': 1
                }
                headers = {'User-Agent': 'MyInstagramClone/1.0 (iskandarovfirdavs09@gmail.com)'}
                r = requests.get('https://nominatim.openstreetmap.org/search', params=params, headers=headers,
                                 timeout=5)
                r.raise_for_status()
                data = r.json()
                if data:
                    cleaned['latitude'] = data[0].get('lat')
                    cleaned['longitude'] = data[0].get('lon')
                else:
                    raise ValidationError("Couldn't resolve coordinates for the entered location.")
            except requests.RequestException:
                raise ValidationError("Error resolving location. Try again later.")
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        lat = self.cleaned_data.get('latitude')
        lon = self.cleaned_data.get('longitude')

        if lat and lon:
            try:
                instance.latitude = float(lat)
                instance.longitude = float(lon)
            except ValueError:
                raise ValidationError("Invalid latitude/longitude.")

        instance.location_name = self.cleaned_data.get('location_name') or None

        if commit:
            instance.save()

            hashtags_text = self.cleaned_data.get('hashtags', '')
            for tag in hashtags_text.split():
                tag = tag.strip('#')
                if tag:
                    hashtag_obj, _ = HashtagModel.objects.get_or_create(name=tag)
                    instance.hashtags.add(hashtag_obj)

            music = self.cleaned_data.get('music')
            if music:
                instance.music.set(music)

        return instance

