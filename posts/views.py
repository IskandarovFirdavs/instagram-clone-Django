from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from posts.forms import PostModelForm
from posts.models import PostModel


from collections import defaultdict

def home_view(request):
    posts = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Post).order_by('-created_at')
    histories = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.History).order_by('-created_at')

    grouped_histories = defaultdict(list)
    for history in histories:
        grouped_histories[history.userID].append(history)

    return render(request, 'home.html', {
        'posts': posts,
        'grouped_histories': grouped_histories.items()
    })


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostModelForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.userID = request.user
            post.save()
            form.save_m2m()
            return redirect('profile')

    else:
        form = PostModelForm(instance=request.user)

    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'create.html', context)


class DirectView(TemplateView):
    template_name = 'direct.html'


def explore_view(request):
    posts = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Post ).order_by('-created_at')
    reels = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Reels).order_by('-created_at')
    return render(request, 'explore.html', {
        'posts': posts,
        'reels': reels
    })





class MessagesView(TemplateView):
    template_name = 'messages.html'


class NotificationsView(TemplateView):
    template_name = 'notifications.html'


class ReelsView(TemplateView):
    template_name = 'reels.html'


class SearchView(TemplateView):
    template_name = 'search.html'
