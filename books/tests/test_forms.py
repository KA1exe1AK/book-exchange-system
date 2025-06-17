from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from books.forms import BookForm
from books.models import Genres
from users.models import User

class BookFormTest(TestCase):

    def setUp(self):
        self.genre = Genres.objects.create(name="Fantasy")
        self.user = User.objects.create(username="testuser")
        self.image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

    def test_book_form_valid(self):
        form_data = {
            'name': 'New Book',
            'author': 'New Author',
            'city': 'New City',
            'genre': self.genre.id,
            'status': 'Available',
            'image': self.image,  # Добавляем изображение
            'owner': self.user.id  # Добавляем владельца
        }
        form = BookForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), msg=form.errors)  # Печать ошибок для отладки

    def test_book_form_invalid(self):
        form_data = {'name': '', 'author': ''}
        form = BookForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
