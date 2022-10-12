from django.test import Client, TestCase
from django.urls import reverse


class UrlsTestAbout(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pagess_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
