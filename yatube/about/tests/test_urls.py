from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class UrlsTestAbout(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_tech_exists_at_desred_location(self):
        """Проверка доступности адресов в приложении about"""
        templates_url_names = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
        }
        for address, status in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)
