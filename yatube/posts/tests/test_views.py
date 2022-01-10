from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post_author = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.post_author,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.post_author)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html',
            reverse('posts:profile', kwargs={'username': self.user}):
            'posts/profile.html',
        }
        for adress, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_author.get(adress)
                self.assertTemplateUsed(response, template)

    def test_create_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильной формой."""
        response = self.authorized_client_author.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильной формой."""
        response = self.authorized_client_author.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
                    'posts:index')))
        self.assertEqual(response.context.get('page_obj')[0], self.post)

    def test_group_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
                    'posts:group_list', kwargs={'slug': self.group.slug})))
        self.assertEqual(response.context.get('group'), self.group)
        self.assertEqual(response.context.get('page_obj')[0], self.post)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
                    'posts:profile', kwargs={'username': self.user})))
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(response.context.get('page_obj')[:0], [])

    def test_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
                    'posts:post_detail', kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context.get('post'), self.post)

    def test_user_is_not_author(self):
        """Пользователь не автор поста"""
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/', follow=True
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_user_can_comment(self):
        """Комментировать может только авторизованный"""
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/comment/', follow=True
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_guest_cant_comment(self):
        """Незарегестированный пользователь не может комментировать"""
        response = self.guest_client.get(
            f'/posts/{self.post.id}/comment/', follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/')

    def test_follow(self):
        """Авторизованный пользователь может подписываться"""
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow', kwargs={'username': self.post_author}
            )
        )
        follow = Follow.objects.get(
            user=self.user,
            author=self.post_author,
        )
        follow_count_upd = Follow.objects.count()
        follow.refresh_from_db()
        self.assertEqual(follow_count_upd, follow_count + 1)
        self.assertEqual(follow.user, self.user)
        self.assertEqual(follow.author, self.post_author)

    def test_unfollow(self):
        """Авторизованный пользователь может отписываться"""
        follow_count = Follow.objects.count()
        Follow.objects.create(
            user=self.user,
            author=self.post_author,
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow', kwargs={'username': self.post_author}
            )
        )
        follow_count_upd = Follow.objects.count()
        self.assertEqual(follow_count_upd, follow_count)

    def test_cant_follow_youself(self):
        """Пользователь не может подписаться на себя"""
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user})
        )
        follow_count_upd = Follow.objects.count()
        self.assertEqual(follow_count_upd, follow_count)

    def test_new_post_of_follow(self):
        """Новая запись появляется в ленте тех кто подписан"""
        Follow.objects.create(
            user=self.user,
            author=self.post_author,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(response.context.get('page_obj')[0], self.post)

    def test_new_post_if_unfollow(self):
        """Новая запись не появляется в ленте кто не подписан"""
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(response.context.get('page_obj')[:0], [])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.POST_COUNT = settings.OBJECTS_PER_PAGE + 3
        cls.post = [
            Post(
                text=f'Пост №{num}',
                author=cls.user,
                group=cls.group,
            )
            for num in range(cls.POST_COUNT)
        ]
        Post.objects.bulk_create(cls.post)
        cache.clear()

    def test_paginator_on_pages_with_post(self):
        """Проверка пагинатора с 13 постами"""
        first_page_amount = settings.OBJECTS_PER_PAGE
        second_page_amount = self.POST_COUNT - settings.OBJECTS_PER_PAGE
        paginator_urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        ]
        for revers in paginator_urls:
            with self.subTest(revers=revers):
                self.assertEqual(len(
                    self.client.get(revers).context.get(
                        'page_obj')), first_page_amount
                )
                self.assertEqual(len(
                    self.client.get(revers + '?page=2').context.get(
                        'page_obj')), second_page_amount
                )


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='Author')
        cls.post = Post.objects.create(
            author=cls.post_author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.post_author)

    def test_cache(self):
        """Проверка кэша"""
        response = self.client.get(reverse('posts:index'))
        self.post.delete()
        post_delete = self.client.get(reverse('posts:index'))
        self.assertEqual(response.content, post_delete.content)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, post_delete.content)
