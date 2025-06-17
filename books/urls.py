from django.urls import path
from django.conf.urls.static import static#new
from django.conf import settings#new


from books import views
app_name = 'books'

urlpatterns = [
    path('<slug:genre_slug>/', views.catalog, name='index'),
    path('book/<slug:book_slug>/', views.book, name='book'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)#new