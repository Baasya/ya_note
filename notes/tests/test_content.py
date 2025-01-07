from notes.forms import NoteForm

from django.urls import reverse
from .base_test_class import TestBaseCase


class TestContent(TestBaseCase):
    """Тестирование контента."""

    def test_notes_in_object_list(self):
        """.

        Отдельная заметка передаётся на страницу со списком заметок в списке
        object_list, в словаре context.

        В список заметок одного пользователя не попадают заметки другого
        пользователя.

        """
        users_values = (
            (self.author, True),
            (self.reader, False),
        )
        for user, value in users_values:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertEqual(self.note in object_list, value)

    def test_authorized_client_has_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
