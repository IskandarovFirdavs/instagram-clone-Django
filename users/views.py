from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView

from posts.models import PostModel, NotificationModel
from users.forms import RegisterForm, LoginForm, UserUpdateForm
from django.contrib.auth import authenticate, login, logout

from users.models import UserModel, Follow


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
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    posts = PostModel.objects.filter(userID=request.user, post_type=PostModel.PostTypeChoice.Post).order_by(
        '-created_at')
    reels = PostModel.objects.filter(userID=request.user, post_type=PostModel.PostTypeChoice.Reels).order_by(
        '-created_at')

    qs = UserModel.objects.exclude(id=request.user.id).order_by('username')

    if request.method == "POST":
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('profile')

    else:
        form = UserUpdateForm(instance=request.user)

    print("FILES:", request.FILES)
    print("POST:", request.POST)
    print("Is multipart?", request.content_type.startswith('multipart'))

    return render(request, 'profile.html', {
        'user': request.user,
        "users": qs,
        'posts': posts,
        'reels': reels,
        "form": form,
    })


def another_user_profile_view(request, pk):
    user = UserModel.objects.get(pk=pk)
    posts = PostModel.objects.filter(userID=user, post_type=PostModel.PostTypeChoice.Post).order_by('-created_at')
    reels = PostModel.objects.filter(userID=user, post_type=PostModel.PostTypeChoice.Reels).order_by('-created_at')

    return render(request, 'another_profile.html', {
        'user': user,
        'posts': posts,
        'reels': reels,
    })


@login_required
def follow_view(request, pk):
    following_to = get_object_or_404(UserModel, pk=pk)
    user = request.user
    followers = Follow.objects.filter(follower=user, following=following_to)

    is_self_like = (following_to == user)

    if followers:
        if not is_self_like:
            followers.delete()
            NotificationModel.objects.filter(
                liked_by=user
            ).delete()
    else:
        if not is_self_like:
            Follow.objects.create(follower=user, following=following_to)
            if following_to and following_to.pk:
                try:
                    obj, created = NotificationModel.objects.get_or_create(
                        comment_like=None,
                        liked_by=user,
                        owner=following_to,
                        post_like=None,
                        reply_comment_like=None
                    )
                    print("Notification created:", created)
                except IntegrityError as e:
                    print("❌ Notification creation failed:", str(e))
            else:
                print("⚠️ Skipped: Post owner is invalid")


    return redirect(request.GET.get('next', '/'))


class UserListView(ListView):
    template_name = 'search.html'
    context_object_name = 'users'

    def get_queryset(self):
        qs = UserModel.objects.exclude(id=self.request.user.id)
        q = self.request.GET.get('q')

        if q:
            qs = qs.filter(username__icontains=q)

        return qs


def followers_list_view(request, pk):
    user = get_object_or_404(UserModel, pk=pk)
    followers = user.follower_set.all()
    qs = UserModel.objects.exclude(pk=request.user.pk).order_by('username')

    context = {
        'usr': user,
        'followers': followers,
        'users': qs
    }
    return render(request, 'followers.html', context)


def followings_list_view(request, pk):
    user = get_object_or_404(UserModel, pk=pk)
    followings = user.following_set.all()
    qs = UserModel.objects.exclude(pk=request.user.pk).order_by('username')

    context = {
        'usr': user,
        'followings': followings,
        'users': qs
    }
    return render(request, 'followings.html', context)
