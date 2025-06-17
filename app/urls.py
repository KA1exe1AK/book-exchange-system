from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse
from prometheus_client import generate_latest

def metrics_view(request):
    data = generate_latest()
    return HttpResponse(data, content_type='text/plain')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace='main')),
    path('catalog/', include('books.urls', namespace='catalog')),
    path('user/', include('users.urls', namespace='user')),
    path('fav/', include('favs.urls', namespace='fav')),
    path('metrics', metrics_view, name='prometheus-metrics'),
    path('__debug__/', include('debug_toolbar.urls')),

]