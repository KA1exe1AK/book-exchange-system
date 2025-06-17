from django.contrib import admin

from books.models import Genres, Books

from users.models import User

# admin.site.register(Genres)
admin.site.register(User)

@admin.register(Genres)
class GenresAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
