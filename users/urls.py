from django.urls import path

from users import views

app_name = 'users'

urlpatterns = [
    path('login', views.login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('profile/', views.profile, name='profile'),
    path('users-fav/', views.users_fav, name='users_fav'),
    path('logout/', views.logout, name='logout'),
    path('add_book/', views.add_book, name='add_book'),
    path('my_books/', views.my_books, name='my_books'),
    path('delete_book/<uuid:book_id>/', views.delete_book, name='delete_book'),
]