from django.db import models

from books.models import Books
from users.models import User



class Fav(models.Model):

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Пользователь')
    book = models.ForeignKey(to=Books, on_delete=models.CASCADE, verbose_name='Книга')
    session_key = models.CharField(max_length=32, null=True, blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        db_table = 'fav'
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"



    def __str__(self):
        return f'Избранное {self.user.username} | Книга {self.book.name}'
