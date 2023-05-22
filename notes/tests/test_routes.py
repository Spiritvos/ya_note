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
            slug='Test',
            author=cls.author
        )

    # Главная страница доступна анонимному пользователю.
    # Страницы регистрации пользователей, входа в учётную запись
    # и выхода из неё доступны всем пользователям.
    def test_pages_availability(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for url_name in urls:
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # Аутентифицированному пользователю доступна страница со
    # списком заметок _notes/,_ страница успешного добавления заметки
    # _done/_, страница добавления новой заметки _add/._
    def test_availability_for_add_delete_note(self):
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        for url_name in urls:
            self.client.force_login(self.reader)
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # Страницы отдельной заметки, удаления и редактирования заметки доступны
    # только автору заметки. Если на эти страницы попытается
    # зайти другой пользователь — вернётся ошибка 404.
    def test_availability_edit_and_delete_note(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            urls = (
                ('notes:detail', (self.note.slug,)),
                ('notes:edit', (self.note.slug,)),
                ('notes:delete', (self.note.slug,)),
            )
            for url_name, args in urls:
                with self.subTest(user=user, url_name=url_name, args=args):
                    url = reverse(url_name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    # При попытке перейти на страницу списка заметок, страницу успешного
    # добавления записи, страницу добавления заметки, отдельной заметки,
    # редактирования или удаления заметки анонимный пользователь
    # перенаправляется на страницу логина.
    def test_redirect_for_anonymous_client(self):
        login_url = reverse(
            'users:login'
        )
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for url_name, args in urls:
            with self.subTest(url_name=url_name, args=args):
                url = reverse(url_name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
