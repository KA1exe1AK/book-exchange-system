from django.db.models import Q

from books.models import Books

def q_search(query):
    if query.isdigit() and len(query) <= 5:
        return Books.object.filter(id = int(query))
    
    keywords = [word for word in query.split() ]

    q_objects = Q()
    for token in keywords:
        q_objects |= Q(description_icontains=token)
        q_objects |= Q(name_icontains=token)
        q_objects |= Q(author_icontains=token)

    return Books.objects.filter(q_objects)