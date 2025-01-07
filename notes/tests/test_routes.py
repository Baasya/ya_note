from http import HTTPStatus

from django.urls import reverse

from .base_test_class import TestBaseCase


class TestRoutes(TestBaseCase):
    """Тестирование маршрутов."""

    def test_pages_availability_for_everyone(self):
        """
        Главная страница доступна анонимному пользователю.Cтраницы регистрации
        пользователелей, входа в учётную запись и выхода из неё доступны
        всем пользователям.
        """
        urls = (
                ('notes:home', None),
                ('users:login', None),
                ('users:logout', None),
                ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_users(self):
        """
        Аутентифицированную пользователю доступны:
        страница со списком заметок notes/,
        страница успешного добавления заметки done/,
        страница добавления новой заметки add/.
        """
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_detail_edit_and_delete(self):
        """
        Страницы отдельной заметки, удаления и редактирования заметки доступны
        только автору заметки.Если на эти страницы попытается зайти другой
        пользователь — вернётся ошибка 404.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        При попытке перейти на страницу списка заметок, страницу успешного
        добавления записи, страницу добавления заметки, отдельной заметки,
        редактирования или удаления заметки анонимный пользователь
        перенаправляется на страницу логина.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:delete', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
