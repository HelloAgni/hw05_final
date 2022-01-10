from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post_author = User.objects.create_user(username='Author')
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.post_author)

    def test_about(self):
        """URL-адрес about использует соответствующий шаблон."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_author.get(adress)
                self.assertTemplateUsed(response, template)
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_about_page_author(self):
        """Запрос автора к странице вернет статус 200"""
        response = self.authorized_client_author.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_user(self):
        """Запрос пользователя к странице вернет статус 200"""
        response = self.authorized_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_guest(self):
        """Запрос гостя к странице вернет статус 200"""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
