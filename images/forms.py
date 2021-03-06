from urllib import request

from django import forms
from django.utils.text import slugify
from django.core.files.base import ContentFile

from .models import Image


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'url', 'description')
        widgets = {
            'url': forms.HiddenInput,
        }

    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ('jpg', 'jpeg')
        extension = self.get_extension(url)
        if extension not in valid_extensions:
            raise forms.ValidationError('The given URL doesn\'t math valid image extensions.')
        return url

    def save(self, commit=True) -> Image:
        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        name = slugify(image.title)
        extension = self.get_extension(image_url)
        image_name = f'{name}.{extension}'

        response = request.urlopen(image_url)
        image.image.save(image_name, ContentFile(response.read()), save=False)

        if commit:
            image.save()

        return image

    @staticmethod
    def get_extension(name: str) -> str:
        return name.rsplit('.', 1)[1].lower()
