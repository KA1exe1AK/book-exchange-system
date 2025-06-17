from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from books import views
from django_prometheus.exports import ExportToDjangoView


app_name = 'catalog'

urlpatterns = [
    path('', views.catalog, name='index'), 
    path('fantastika/', views.catalog, name='fantastika'),
    path('book/<slug:book_slug>/', views.book, name='book'), 
    path('<slug:genre_slug>/', views.catalog, name='index'),
    path('book/create/', views.create_book, name='create_book'),
    path('book/<slug:book_slug>/update/', views.update_book, name='update_book'),
    path('book/<slug:book_slug>/delete/', views.delete_book, name='delete_book'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)