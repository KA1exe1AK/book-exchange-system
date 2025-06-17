from django.shortcuts import redirect, render

from books.models import Books
from favs.models import Fav

def fav_add(request, book_slug):
    book = Books.objects.get(slug=book_slug)

    if request.user.is_authenticated:
        favs = Fav.objects.filter(user=request.user, book=book)

        if favs.exists():
            fav = favs.first()
            if fav:
                fav.save()
        else:
            Fav.objects.create(user=request.user, book=book)

    return redirect(request.META['HTTP_REFERER'])

def fav_remove(request, fav_id):

    fav = Fav.objects.get(id=fav_id)
    fav.delete()


    return redirect(request.META['HTTP_REFERER'])
