from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from posts.models import PostModel
from users.forms import RegisterForm, LoginForm, UserUpdateForm
from django.contrib.auth import authenticate, login, logout

from users.models import UserModel


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                form.add_error(None, 'Username or password id invalid')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form} )


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    posts = PostModel.objects.filter(userID=request.user, post_type=PostModel.PostTypeChoice.Post).order_by('-created_at')
    reels = PostModel.objects.filter(userID=request.user,  post_type=PostModel.PostTypeChoice.Reels).order_by('-created_at')

    if request.method == "POST":
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('profile')

    else:
        form = UserUpdateForm(instance=request.user)



    return render(request, 'profile.html', {
        'user': request.user,
        'posts': posts,
        'reels': reels,
    })


class UserListView(ListView):
    template_name = 'search.html'
    context_object_name = 'users'

    def get_queryset(self):
        qs = UserModel.objects.exclude(id=self.request.user.id).order_by('username')
        q = self.request.GET.get('q')

        if q:
            qs = qs.filter(username__icontains=q)

        return qs



def another_user_profile_view(request, pk):
    user = UserModel.objects.get(id=pk)
    posts = PostModel.objects.filter(userID=user, post_type=PostModel.PostTypeChoice.Post).order_by('-created_at')
    reels = PostModel.objects.filter(userID=user,  post_type=PostModel.PostTypeChoice.Reels).order_by('-created_at')


    return render(request, 'profile.html', {
        'user': user,
        'posts': posts,
        'reels': reels,
    })
