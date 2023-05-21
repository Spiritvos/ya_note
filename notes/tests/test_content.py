from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
    LIST_URL = reverse('notes:list')
    
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Норм чел')
        cls.reader = User.objects.create(username='Алёша')
        cls.note_1 = Note.objects.create(
            title='Тестовый заголовок',
            text='Кокой-то текст',
            slug='Test',
            author=cls.author
        )
        cls.note_2 = Note.objects.create(
            title='Тестовый заголовок_2',
            text='Кокой-то текст_2',
            slug='Test2',
            author=cls.reader
        )


    # В список заметок одного пользователя не попадают 
    # заметки другого пользователя
    def test_autor_list_note(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        single_note = Note.objects.all().filter(author=self.reader)[0]
        self.assertNotIn(single_note, object_list)


    # Отдельная заметка передаётся на страницу со списком заметок в 
    # списке object_list в словаре context.
    def test_unique_note(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        single_note = Note.objects.all().filter(author=self.author)[0]
        self.assertIn(single_note, object_list)


    # На страницы создания и редактирования заметки передаются формы.
    def test_access_client_form(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note_1.slug,)),
        )
        for url_name, args in urls:
            with self.subTest(url_name=url_name, args=args):
                url = reverse(url_name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
