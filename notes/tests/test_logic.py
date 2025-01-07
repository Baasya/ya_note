from http import HTTPStatus

from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

from .base_test_class import TestBaseCase


class TestLogic(TestBaseCase):
    """Тестирование логики."""

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        Note.objects.all().delete()
        self.client.post(self.URL_NOTE_ADD, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        self.client.force_login(self.author)
        Note.objects.all().delete()
        response = self.client.post(self.URL_NOTE_ADD, data=self.form_data)
        self.assertRedirects(response, self.URL_NOTE_SUCCESS)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_unique_slug(self):
        """Невозможно создать неуникальный slug."""
        self.client.force_login(self.author)
        notes_amount = Note.objects.count()
        slug_repeat_data = {
            'title': 'Заголовок1',
            'text': 'Текст1',
            'slug': 'Slug',
        }
        response = self.client.post(self.URL_NOTE_ADD, data=slug_repeat_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING)
        )
        notes_new_amount = Note.objects.count()
        self.assertEqual(notes_amount, notes_new_amount)

    def test_auto_slug(self):
        """
        Если при создании заметки не заполнен slug,
        то он формируется автоматически,
        с помощью функции pytils.translit.slugify.
        """
        self.client.force_login(self.author)
        Note.objects.all().delete()
        without_slug_data = {
            'title': 'Заголовок33',
            'text': 'Текст33',
        }
        response = self.client.post(self.URL_NOTE_ADD, data=without_slug_data)
        self.assertRedirects(response, self.URL_NOTE_SUCCESS)
        notes_amount = Note.objects.count()
        self.assertEqual(notes_amount, 1)
        new_note = Note.objects.get()
        auto_slug = slugify(without_slug_data['title'])
        self.assertEqual(new_note.slug, auto_slug)

    def test_author_can_delete_note(self):
        """Автор может удалить заметку."""
        self.client.force_login(self.author)
        response = self.client.delete(self.URL_DELETE)
        self.assertRedirects(response, self.URL_NOTE_SUCCESS)
        note_new_amount = Note.objects.count()
        self.assertEqual(note_new_amount, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        self.client.force_login(self.reader)
        response = self.client.delete(self.URL_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Автор может редактировать заметку."""
        self.client.force_login(self.author)
        response = self.client.post(self.URL_EDIT, data=self.form_data)
        self.assertRedirects(response, self.URL_NOTE_SUCCESS)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_user_cant_edit_comment_of_another_user(self):
        """Пользователь не может редактировать чужую заметку."""
        self.client.force_login(self.reader)
        response = self.client.post(self.URL_EDIT, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        note_object = Note.objects.get()
        self.assertEqual(self.note.title, note_object.title)
        self.assertEqual(self.note.text, note_object.text)
        self.assertEqual(self.note.slug, note_object.slug)
