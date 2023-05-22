from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Алёша')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Кокой-то текст',
            'slug': '',
            'author': cls.user
        }

    # Если при создании заметки не заполнен slug, то он формируется
    # автоматически, с помощью функции pytils.translit.slugify.
    def test_slug_empty_field(self):
        prepare_slug = slugify(self.form_data['title'])[:100]
        self.auth_client.post(self.url, data=self.form_data)
        name_slug_note = Note.objects.first().slug
        self.assertEqual(name_slug_note, prepare_slug)

    # Анонимный пользователь не может создать заметку.
    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    # Залогиненный пользователь может создать заметку.
    def test__user_can_create_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):
    NEW_NOTE_TEXT = 'Новый какой-то текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Норм чел')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Алёша')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Тестовый заголовок',
            text='Кокой-то текст',
            slug='Test',
            author=cls.author
        )
        cls.url = reverse('notes:add')
        cls.edit_note = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_note = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.note.title,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.note.slug,
            'author': cls.author
        }

    # Невозможно создать две заметки с одинаковым slug.
    def test_dublicate_slug_field(self):
        WARNING_MSG = f'{self.note.slug}{WARNING}'
        dublicate_slug_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': self.note.slug,
            'author': self.author
        }
        response = self.author_client.post(self.url, data=dublicate_slug_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=WARNING_MSG
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    # Пользователь может удалять свои заметки.
    def test_author_can_delete_note(self):
        self.author_client.delete(self.delete_note)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    # Пользователь не может удалять чужие заметки.
    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    # Пользователь может редактировать свои заметки
    def test_author_can_edit_note(self):
        self.author_client.post(self.edit_note, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    # Пользователь не может редактировать чужие заметки
    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_note, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.text, self.NEW_NOTE_TEXT)
