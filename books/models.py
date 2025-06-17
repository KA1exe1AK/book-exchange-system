from django.db import models
import uuid
from slugify import slugify

from users.models import User

class Genres(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')

    class Meta:
        db_table = 'books_genres'
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name

class Books(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150,  verbose_name='Название')
    author = models.CharField(max_length=150, verbose_name='Автор')
    slug = models.SlugField(max_length=200, blank=True, null=True, verbose_name='URL')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    image = models.ImageField(upload_to='books_images',blank=True, null=True, verbose_name='Изображение')
    city = models.CharField(max_length=150, verbose_name='Город')
    owner = models.ForeignKey(to = User, on_delete=models.PROTECT, verbose_name='Владелец')
    status = models.CharField(max_length=150, verbose_name='Статус')
    genre = models.ForeignKey(to=Genres, on_delete=models.PROTECT, verbose_name='Жанр')


    class Meta:
        db_table = 'book'
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = (['id'])

    def __str__(self):
        return self.name
    
    def display_id(self):
        return f"{self.id:05}"
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    
    


