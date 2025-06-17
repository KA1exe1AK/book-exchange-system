from django.shortcuts import render
from django.core.paginator import Paginator

from books.models import Books
from books.utils import q_search


def catalog(request, genre_slug=None):

    page = request.GET.get('page', 1)
    query = request.GET.get('q', None)

    if genre_slug == 'all':
        books = Books.objects.all()
    elif query:
        books = q_search()
    else:
        books = Books.objects.filter(genre__slug=genre_slug)


    paginator = Paginator(books, 3)
    current_page = paginator.page(int(page))

    context = {
        'title': 'Каталог',
        'books': current_page,
    }
    return render(request, 'books/catalog.html', context)

def book(request, book_slug):
    book = Books.objects.get(slug = book_slug)

    context = {
        'book' : book
    }
    return render(request, 'books/book.html', context=context)



