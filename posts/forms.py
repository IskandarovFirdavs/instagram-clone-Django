from django import forms

from posts.models import PostModel, MusicModel, HashtagModel, CommentModel


class PostModelForm(forms.ModelForm):
    location = forms.CharField(max_length=40)
    hashtags = forms.CharField(required=False, )
    music = forms.ModelMultipleChoiceField(queryset=MusicModel.objects.all(), required=False)

    class Meta:
        model = PostModel
        fields = ['caption', 'post_type', 'contentUrl', 'location']

    def save(self, commit=True):
        instance = super().save(commit=False)

        location = self.cleaned_data['location']
        parts = location.split(',')
        if len(parts) == 2:
            try:
                instance.latitude = float(parts[0].strip())
                instance.longitude = float(parts[1].strip())
            except ValueError:
                raise forms.ValidationError("Invalid location format. Use 'lat, long'.")
        else:
            raise forms.ValidationError("Location must be in 'latitude,longitude' format.")

        if commit:
            instance.save()

            hashtags_text = self.cleaned_data.get('hashtags', '')
            for tag in hashtags_text.split():
                tag = tag.strip('#')
                if tag:
                    hashtag_obj, created = HashtagModel.objects.get_or_create(name=tag)
                    instance.hashtags.add(hashtag_obj)

            music = self.cleaned_data.get('music')
            if music:
                instance.music.set(music)

        return instance
