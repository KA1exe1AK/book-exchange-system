from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages


from books.models import Books
from users.forms import ProfileForm, UserLoginForm, UserRegistrationForm
from books.forms import BookForm

def login(request):

    if request.method == "POST":

        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                messages.success(request, f"{username}, Вы вошли в аккаунт")
                redirect_page = request.POST.get('next', None)
                if redirect_page and redirect_page != reverse('user:logout'):
                    return HttpResponseRedirect(request.POST.get('next'))

                return HttpResponseRedirect(reverse('main:index'))
    else:
        form = UserLoginForm()

    context = { 
        'title': 'Авторизация',
        'form': form,
    }
    return render(request, 'users/login.html', context)



def registration(request):
    if request.method == 'POST':
            form = UserRegistrationForm(data=request.POST)
            if form.is_valid():
                form.save()
                user = form.instance
                auth.login(request, user)
                messages.success(request, f"{user.username}, Вы успешно зарегистрированы и вошли в аккаунт")
                return HttpResponseRedirect(reverse('main:index'))
    else:
        form = UserRegistrationForm()

    context = {
        'title': 'Регистрация',
        'form': form
    }
    return render(request, 'users/registration.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=request.user, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Профайл успешно обновлен")
            return HttpResponseRedirect(reverse('user:profile'))
    else:
        form = ProfileForm(instance=request.user)

    context = {
        'title': 'Личный Кабинет',
        'form': form
    }
    return render(request, 'users/profile.html', context)

@login_required
def logout(request):
    messages.success(request, f"{request.user.username}, Вы вышли из аккаунта")
    auth.logout(request)
    return redirect(reverse('main:index'))

def users_fav(request):
    return render(request, 'users/users_fav.html')

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            book = form.save(commit=False)
            book.save()
            return redirect('users:profile')
    else:
        form = BookForm(user=request.user) 
    return render(request, 'users/add_book.html', {'form': form}) 

@login_required
def delete_book(request, book_id):
    book = Books.objects.get(pk=book_id)
    if book.owner == request.user:  # Проверка, что пользователь владеет книгой
        book.delete()
        return redirect('users:profile')  # Перенаправьте на профиль пользователя
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def my_books(request):
    books = Books.objects.filter(owner=request.user)  # Получаем книги текущего пользователя
    return render(request, 'users/my_books.html', {'books': books})
