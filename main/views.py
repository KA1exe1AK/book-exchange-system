from django.http import HttpResponse
from django.shortcuts import render

from books.models import Genres

def index(request):

    context = { 
        'title': 'Главная',
        'content': 'Сервис для обмена книгами',
    }
    return render(request, 'main/index.html', context)

def about(request):
    context = { 
        'title': 'О нас',
        'content': 'О нас',
        'text_on_page': "Класс класс"
    }
    return render(request, 'main/about.html', context)
