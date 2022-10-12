from http import HTTPStatus
import tempfile
import shutil

from django.test import Client, TestCase, override_settings
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='FormAuth')
        cls.user_2 = User.objects.create_user(username='ImageUser')
        cls.group = Group.objects.create(
            title='группа формы',
            slug='form_slug',
            description='описание формы',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(FormTest.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(FormTest.user_2)

    def test_create_post(self):
        """при создания поста создаётся новая запись в базе данных"""
        tasks_post_count = Post.objects.count()
        form_data = {
            'text': 'Текст для теста форм',
            'group': FormTest.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), tasks_post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст для теста форм',
                group=FormTest.group
            ).exists()
        )

    def test_create_post_edit(self):
        """при редактировании поста происходит изменение в базе данных."""
        self.post = Post.objects.create(
            author=FormTest.user,
            text='Тестовый текст',
            group=self.group,
        )
        self.test_group = Group.objects.create(
            title='W2',
            slug='test_slug_2',
            description='Тестовое описание_2'
        )
        form_data = {
            'text': 'Текст для теста форм_2',
            'group': self.test_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text='Текст для теста форм_2',
                group=self.test_group.id,
            ).exists()
        )
        self.assertFalse(
            Post.objects.filter(
                text='Текст для теста форм_2',
                group=self.group,
            ).exists()
        )

    def test_post_edit_for_guest_client(self):
        """Страница create_post недоступна неавторизованному клиенту"""
        response = self.guest_client.post(
            reverse('posts:post_create'),
            follow=True
        )
        users_login = reverse('users:login')
        post_create = reverse('posts:post_create')
        self.assertRedirects(
            response, f'{users_login}?next={post_create}')

    def test_post_edit_for_guest2_client(self):
        """Страница post_edit недоступна неавторизованному клиенту"""
        self.post = Post.objects.create(
            author=FormTest.user,
            text='Тестовый текст',
            group=self.group,
        )
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            follow=True
        )
        users_login = reverse('users:login')
        post_edit = reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id})
        self.assertRedirects(
            response, f'{users_login}?next={post_edit}')

    def test_title_label(self):
        """labels формы совпадает с ожидаемым."""
        for field, expected_value in FormTest.form.Meta.labels.items():
            with self.subTest(field=field):
                self.assertEqual(
                    FormTest.form.fields[field].label, expected_value)

    def test_title_help_text(self):
        """help_text формы совпадает с ожидаемым."""
        for field, expected_value in FormTest.form.Meta.help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    FormTest.form.fields[field].help_text, expected_value)

    def test_form_image(self):
        """Валидная форма создает запись в базе данных."""
        tasks_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client_2.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                image='posts/small.gif'
            ).exists()
        )

    def test_add_comment(self):
        """Страница posts/<int:post_id>/comment/
            недоступна неавторизованному клиенту"""
        self.post_comment = Post.objects.create(
            author=FormTest.user,
            text='Тестовый текст',
            group=self.group,
        )
        response = self.guest_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': self.post_comment.id}),
            follow=True
        )
        users_login = reverse('users:login')
        post_comment = reverse(
            'posts:add_comment', kwargs={'post_id': self.post_comment.id})
        self.assertRedirects(
            response, f'{users_login}?next={post_comment}')

    def test_comment_added(self):
        """после успешной отправки комментарий появляется на странице поста."""
        self.post_comment_2 = Post.objects.create(
            author=FormTest.user,
            text='Тестовый текст',
            group=self.group,
        )
        comment = Comment.objects.count()
        form_data = {
            'text': 'Text_comment',
        }
        self.authorized_client_2.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post_comment_2.id}),
            follow=True,
            data=form_data,
        )
        self.assertEqual(Comment.objects.count(), comment + 1)
        self.assertTrue(Comment.objects.filter(text='Text_comment'))
