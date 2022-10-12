from django.forms import ModelForm

from posts.models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        labels = {
            'group': 'Группа',
            'text': 'Текст',
        }
        help_texts = {
            'group': 'Описание группы',
            'text': 'Текст поста',
        }
        fields = ('text', 'group', 'image')


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        labels = {
            'text': 'Текст комментария',
        }
        fields = ('text',)
