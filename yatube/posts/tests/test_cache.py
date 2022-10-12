from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, User


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_cache')

    def setUp(self):
        self.guest_client_cache = Client()

    def test_cahce(self):
        'тест для проверки кеширования главной страницы'
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый текст1_cache',
        )
        response = self.guest_client_cache.get(reverse('posts:index'))
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст1_cache',
            ).exists()
        )
        self.post.delete()
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый текст1_cache',
            ).exists()
        )
        response_new = self.guest_client_cache.get(reverse('posts:index'))
        self.assertEqual(response.content, response_new.content)
        cache.clear()
        response_new_2 = self.guest_client_cache.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_new_2.content)
