from http import HTTPStatus
  

from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Норм чел')
        cls.reader = User.objects.create(username='Алёша')
        cls.note = Note.objects.create(
            title='Тестовый заголовок',
            text='Кокой-то текст',
            slug='Тестовая категория',
            author=cls.reader
        )
        
    
    def test_pages_availability(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
    
    