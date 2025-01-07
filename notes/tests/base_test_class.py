from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestBaseCase(TestCase):
    """Общие данные для тестов."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестирования."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Slug',
            author=cls.author
        )

        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'Slug',
        }

        cls.URL_NOTE_ADD = reverse('notes:add')
        cls.URL_NOTE_SUCCESS = reverse('notes:success')
        cls.URL_DELETE = reverse('notes:delete', args=(cls.note.slug,))
        cls.URL_EDIT = reverse('notes:edit', args=(cls.note.slug,))
