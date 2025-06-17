from django import template

from favs.models import Fav


register = template.Library()


@register.simple_tag()
def user_favs(request):
    if request.user.is_authenticated:
        return Fav.objects.filter(user=request.user)