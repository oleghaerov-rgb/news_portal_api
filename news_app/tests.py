from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import News


class NewsPortalTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            password='StrongPass123!',
            first_name='Ivan',
            last_name='Petrov',
            email='author@example.com',
        )
        self.other_user = User.objects.create_user(
            username='reader',
            password='StrongPass123!',
            email='reader@example.com',
        )
        self.news = News.objects.create(
            title='Большая городская новость',
            summary='Краткое описание городской новости',
            content='Подробный текст новости с достаточным количеством символов.',
            author=self.author,
        )

    def test_registration_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'new_user',
                'first_name': 'Anna',
                'last_name': 'Ivanova',
                'email': 'anna@example.com',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
        )

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='new_user').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(username='new_user').id)

    def test_news_create_requires_login(self):
        response = self.client.get(reverse('news_create'))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('news_create')}")

    def test_logged_in_user_creates_news_as_author(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse('news_create'),
            {
                'title': 'Новая важная публикация',
                'summary': 'Короткое описание новой публикации',
                'content': 'Полный текст новой публикации с достаточным количеством символов.',
            },
        )

        created_news = News.objects.get(title='Новая важная публикация')
        self.assertEqual(created_news.author, self.author)
        self.assertRedirects(response, reverse('news_detail', args=[created_news.id]))

    def test_only_author_can_edit_news(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse('news_edit', args=[self.news.id]),
            {
                'title': 'Чужое изменение',
                'summary': 'Чужое описание новости',
                'content': 'Чужой текст новости с достаточным количеством символов.',
            },
        )

        self.assertEqual(response.status_code, 403)
        self.news.refresh_from_db()
        self.assertEqual(self.news.title, 'Большая городская новость')

    def test_only_author_can_delete_news(self):
        self.client.force_login(self.other_user)

        response = self.client.post(reverse('news_delete', args=[self.news.id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(News.objects.filter(id=self.news.id).exists())


class NewsAPITests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='api_author',
            password='StrongPass123!',
            email='api_author@example.com',
        )
        self.other_user = User.objects.create_user(
            username='api_reader',
            password='StrongPass123!',
            email='api_reader@example.com',
        )
        self.news = News.objects.create(
            title='API news title',
            summary='API news summary',
            content='This API news content is long enough to pass the serializer validation.',
            author=self.author,
        )

    def test_token_endpoint_returns_token(self):
        response = self.client.post(
            reverse('api_token'),
            {
                'username': 'api_author',
                'password': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_user_api_registration_creates_user(self):
        response = self.client.post(
            reverse('user-list'),
            {
                'username': 'api_new_user',
                'email': 'api_new_user@example.com',
                'password': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='api_new_user')
        self.assertTrue(user.check_password('StrongPass123!'))
        self.assertNotIn('password', response.data)

    def test_news_api_create_requires_authentication(self):
        response = self.client.post(
            reverse('news-list'),
            {
                'title': 'Unauthorized news',
                'summary': 'Unauthorized summary',
                'content': 'This content is long enough, but anonymous users cannot create news.',
            },
            format='json',
        )

        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_news_api_creates_item_for_authenticated_user(self):
        token = Token.objects.create(user=self.author)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = self.client.post(
            reverse('news-list'),
            {
                'title': 'Created from API',
                'summary': 'Created from API summary',
                'content': 'This API-created news item has enough content for validation.',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_news = News.objects.get(title='Created from API')
        self.assertEqual(created_news.author, self.author)
        self.assertEqual(response.data['author'], self.author.id)

    def test_news_api_filter_by_author(self):
        News.objects.create(
            title='Other user API news',
            summary='Other user API summary',
            content='This other news content is long enough to pass validation.',
            author=self.other_user,
        )

        response = self.client.get(reverse('news-list'), {'author': self.author.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['author'], self.author.id)

    def test_news_api_rejects_short_content(self):
        self.client.force_authenticate(user=self.author)

        response = self.client.post(
            reverse('news-list'),
            {
                'title': 'Valid title',
                'summary': 'Valid summary',
                'content': 'Too short.',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', response.data)

    def test_news_api_only_author_can_update(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            reverse('news-detail', args=[self.news.id]),
            {
                'title': 'Changed by another user',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.news.refresh_from_db()
        self.assertEqual(self.news.title, 'API news title')
