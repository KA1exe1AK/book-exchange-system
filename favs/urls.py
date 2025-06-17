from django.urls import path

from favs import views

app_name = 'favs'

urlpatterns = [
    path('fav_add/<slug:book_slug>/', views.fav_add, name='fav_add'),
    path('fav_remove/<int:fav_id>/', views.fav_remove, name='fav_remove'),
]