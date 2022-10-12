from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class UrlsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(UrlsTest.user)
        cache.clear()

    def test_index_url_exists_at_desred_location(self):
        """Проверка доступности адреса главной странице."""
        response = self.guest_client.get('')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url_exists_at_desred_location(self):
        """Проверка доступности адреса /posts/group/<slug:slug>/."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': UrlsTest.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_url_exists_at_desred_location(self):
        """Проверка доступности адреса /posts/create/
            для неавторизованного пользователя"""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': UrlsTest.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desred_location(self):
        """Проверка доступности адреса /page/about/."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': UrlsTest.user}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_url_exists_at_desred_location(self):
        """Проверка доступности адреса /posts/create/
            для авторизованного пользователя"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_exists_at_desred_location(self):
        """Проверка доступности адреса /posts/post_detail/."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': UrlsTest.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_exists_at_desired_location(self):
        """Проверка недоступности  по несуществующему адресу"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': UrlsTest.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': UrlsTest.user}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': UrlsTest.post.id}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_template_404(self):
        '''страница 404 отдаёт кастомный шаблон.'''
        not_existing_address = reverse(
            'posts:profile', kwargs={'username': 'not_existing_name'})
        response = self.authorized_client.get(not_existing_address)
        self.assertTemplateUsed(response, 'core/404.html')
