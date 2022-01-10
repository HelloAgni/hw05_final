from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache
from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
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
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.post_author)
        self.templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            f'/profile/{self.post_author}/': 'posts/profile.html',
            '/unexisting_page/': 'core/404.html',
        }
        cache.clear()

    def test_unexisting_page_author(self):
        """Запрос автора к несуществующей странице вернет ошибку 404"""
        response = self.authorized_client_author.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_unexisting_page_user(self):
        """Запрос пользователя к несуществующей странице вернет ошибку 404"""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_unexisting_page_guest(self):
        """Запрос гостя к несуществующей странице вернет ошибку 404"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_ok_page_author(self):
        """Запрос автора к странице редактирования вернет статус ОК"""
        response = self.authorized_client_author.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template_author(self):
        """URL-адрес для автора использует соответствующий шаблон."""
        for adress, template in self.templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_author.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_authorized(self):
        """URL-адрес для авторизованного использует соответствующий шаблон."""
        for adress, template in self.templates_url_names.items():
            with self.subTest(template=template):
                if adress != f'/posts/{self.post.id}/edit/':
                    response = self.authorized_client.get(adress)
                    self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_guest(self):
        """URL-адрес для всех клиентов использует соответствующий шаблон."""
        for adress, template in self.templates_url_names.items():
            with self.subTest(template=template):
                if adress != f'/posts/{self.post.id}/edit/' \
                        and adress != '/create/':
                    response = self.guest_client.get(adress)
                    self.assertTemplateUsed(response, template)
