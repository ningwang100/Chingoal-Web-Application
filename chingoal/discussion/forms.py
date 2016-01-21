from django import forms

from django.contrib.auth.models import User
from models import *


class ReplyForm(forms.Form):
    text = forms.CharField(max_length = 500)
    post_time = forms.DateTimeField()
    post_id = forms.IntegerField(min_value = 0)

    def clean(self):
        cleaned_data = super(ReplyForm, self).clean()
        return cleaned_data

    def clean_post_id(self):
        post_id = self.cleaned_data.get('post_id')
        if Post.get_max_id() < post_id:
            raise forms.ValidationError('Post ID out of range!')
        return post_id


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', )


class PostFormForm(forms.Form):
    title = forms.CharField(max_length = 500)
    text = forms.CharField(max_length = 500)
    post_time = forms.DateTimeField()

    def clean(self):
        cleaned_data = super(PostFormForm, self).clean()
        return cleaned_data    
