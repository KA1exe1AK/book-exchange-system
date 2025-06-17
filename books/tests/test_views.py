from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from books.models import Books, Genres
from users.models import User

class BooksViewsTest(TestCase):

    def setUp(self):
        self.genre = Genres.objects.create(name="Fantasy")
        self.user = User.objects.create(username="testuser")
        self.image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.book = Books.objects.create(
            name="Test Book",
            author="Test Author",
            city="Test City",
            genre=self.genre,
            owner=self.user,
            status="Available",
            image=self.image  # Добавляем изображение
        )

    def test_catalog_view(self):
        response = self.client.get(reverse('books:index', args=[self.genre.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Каталог")

    def test_book_view(self):
        response = self.client.get(reverse('books:book', args=[self.book.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.name)
