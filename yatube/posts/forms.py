from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 15, 'cols': 100}),
        }
        labels = {
            'text': 'Текст',
            'group': 'Сообщество',
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Текст'}
        widgets = {
            'text': forms.Textarea(attrs={'rows': 7, 'cols': 70}),
        }
