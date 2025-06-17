from django.test import TestCase
from books.models import Genres, Books
from users.models import User

class BooksModelTest(TestCase):

    def setUp(self):
        self.genre = Genres.objects.create(name="Fantasy")
        self.user = User.objects.create(username="testuser")
        self.book = Books.objects.create(
            name="Test Book",
            author="Test Author",
            city="Test City",
            genre=self.genre,
            owner=self.user,
            status="Available"
        )

    def test_genre_creation(self):
        genre = Genres.objects.get(name="Fantasy")
        self.assertEqual(genre.name, "Fantasy")

    def test_book_creation(self):
        book = Books.objects.get(name="Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertEqual(book.genre.name, "Fantasy")

