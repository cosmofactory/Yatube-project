from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
MAX_TEXT_DISPLAYED = 15


class Post(models.Model):
    """ORM model for posts."""

    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:MAX_TEXT_DISPLAYED]

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'posts'
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Group(models.Model):
    """ORM model for groups which post Posts."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=200)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Creates a comment for Post."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        default_related_name = 'comments'

    def __str__(self):
        return self.text[:MAX_TEXT_DISPLAYED]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.user.id} is following {self.author.id}'

    class Meta:
        unique_together = ('user', 'author',)
