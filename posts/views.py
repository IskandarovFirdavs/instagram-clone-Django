from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView, ListView

from posts.forms import PostModelForm
from posts.models import PostModel, PostLikeModel, CommentModel, CommentLikeModel, ReplyCommentModel, \
    ReplyCommentLikeModel

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
    posts = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Post).order_by('-created_at')
    reels = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Reels).order_by('-created_at')

    return render(request, 'explore.html', {
        'posts': posts,
        'reels': reels
    })


class ExploreView(ListView):
    queryset = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Post).order_by('-created_at')
    template_name = 'explore.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reels'] = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Reels).order_by('-created_at')
        return context


class MessagesView(TemplateView):
    template_name = 'messages.html'


class NotificationsView(TemplateView):
    template_name = 'notifications.html'


def reels_view(request):
    reels = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Reels).order_by('-created_at')

    if request.method == 'POST':
        reel_id = request.POST.get('reel_id')

        try:
            reel = PostModel.objects.get(id=reel_id)
        except (PostModel.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'Reel not found or invalid ID.')
            return redirect('reels')

        # Comment
        comment_text = request.POST.get('comment')
        if comment_text:
            CommentModel.objects.create(
                postID=reel,
                userID=request.user,
                comment=comment_text
            )
            return redirect('reels')

        # Reply
        reply_text = request.POST.get("reply_comment")
        comment_id = request.POST.get('parent_comment_id')
        if reply_text and comment_id:
            try:
                parent_comment = CommentModel.objects.get(id=comment_id)
                ReplyCommentModel.objects.create(
                    reply_comment=reply_text,
                    commentID=parent_comment,
                    userID=request.user,
                )
            except CommentModel.DoesNotExist:
                messages.error(request, 'Parent comment not found.')
            return redirect('reels')

        messages.error(request, 'Comment or reply text cannot be empty')
        return redirect('reels')

    context = {
        'reels': reels
    }
    return render(request, 'reels.html', context)


class SearchView(TemplateView):
    template_name = 'search.html'


def like_create(request, id):
    post = get_object_or_404(PostModel, id=id)

    like = PostLikeModel.objects.filter(postID=post, userID=request.user).first()

    if like:
        like.delete()
    else:
        PostLikeModel.objects.create(postID=post, userID=request.user)

    return redirect(request.GET.get('next', '/'))


def like_comment(request, id):
    comment = get_object_or_404(CommentModel, id=id)

    like = CommentLikeModel.objects.filter(commentID=comment, userID=request.user).first()

    if like:
        like.delete()

    else:
        CommentLikeModel.objects.create(commentID=comment, userID=request.user)

    return redirect(request.GET.get('next', '/'))


def like_reply_comment(request, id):
    comment = get_object_or_404(ReplyCommentModel, id=id)

    like = ReplyCommentLikeModel.objects.filter(commentID=comment, userID=request.user).first()

    if like:
        like.delete()

    else:
        ReplyCommentLikeModel.objects.create(commentID=comment, userID=request.user)

    return redirect(request.GET.get('next', '/'))


class SavedListView(LoginRequiredMixin, ListView):
    template_name = 'saved.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        return self.request.user.saved.order_by('-pk')


@login_required
def create_saved_video(request, id):
    post = get_object_or_404(PostModel, id=id)

    if request.user in post.saved.all():
        post.saved.remove(request.user)

    else:
        post.save.add(request.user)

    post.save()

    return redirect(request.GET.get('next', '/'))
