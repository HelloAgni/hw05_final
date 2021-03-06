from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import CASCADE

User = get_user_model()


class Group(models.Model):
    title = models.CharField('титул', max_length=200)
    slug = models.SlugField('слаг', unique=True)
    description = models.TextField('описание', null=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'текст',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='пост группы',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        'текст комментария',
        help_text='введите комментарий'
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Пост: {self.post}, Автор: {self.author} - {self.text}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='following',
    )

    def __str__(self):
        return f'Автор: {self.author} Фоловер:{self.user}'
