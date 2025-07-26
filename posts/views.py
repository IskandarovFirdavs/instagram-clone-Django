from django.utils import timezone
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView, ListView
from posts.forms import PostModelForm
from posts.models import PostModel, PostLikeModel, CommentModel, CommentLikeModel, ReplyCommentModel, \
    ReplyCommentLikeModel
from collections import defaultdict

from users.models import UserModel, Follow


@login_required(login_url='login')
def home_view(request):
    followed_users = request.user.following_set.all()
    followed_ids = [followed.following.id for followed in followed_users]

    one_month_ago = timezone.now() - timedelta(days=3)
    one_day_ago = timezone.now() - timedelta(days=1)

    base_post_filters = {
        'post_type': PostModel.PostTypeChoice.Post,
        'created_at__gte': one_month_ago
    }

    base_history_filters = {
        'post_type': PostModel.PostTypeChoice.History,
        'created_at__gte': one_day_ago
    }

    if len(followed_ids) > 3:
        base_post_filters['userID__in'] = followed_users
        base_history_filters['userID__in'] = followed_users

        posts = PostModel.objects.filter(
            **base_post_filters
        ).order_by('-created_at').exclude(userID=request.user)

        histories = PostModel.objects.filter(
            **base_history_filters
        ).order_by('-created_at')
    else:
        posts = PostModel.objects.filter(**base_post_filters).order_by('-created_at').exclude(userID=request.user)

        histories = PostModel.objects.filter(**base_history_filters).order_by('-created_at')

    qs = UserModel.objects.exclude(id=request.user.id).order_by('username')


    if request.method == 'POST':
        reply_text = request.POST.get("reply_comment")
        comment_id = request.POST.get('parent_comment_id')

        if reply_text and comment_id:
            try:
                parent_comment = CommentModel.objects.get(id=comment_id)
                ReplyCommentModel.objects.create(
                    postID=parent_comment.postID,
                    reply_comment=reply_text,
                    commentID=parent_comment,
                    userID=request.user,
                )
                messages.success(request, 'Javob muvaffaqiyatli qoʻshildi!')
            except CommentModel.DoesNotExist:
                messages.error(request, 'Javob beriladigan izoh topilmadi.')
            except (ValueError, TypeError):
                messages.error(request, 'Notoʻgʻri izoh IDsi.')
            return redirect('home')

        comment_text = request.POST.get('comment')
        post_id = request.POST.get('post_id')

        if comment_text and post_id:
            try:
                post = PostModel.objects.get(id=post_id)
                CommentModel.objects.create(
                    postID=post,
                    userID=request.user,
                    comment=comment_text
                )
                messages.success(request, 'Izoh muvaffaqiyatli qoʻshildi!')
            except (PostModel.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'Izoh qoʻshishda xato: Post topilmadi yoki ID notoʻgʻri.')
            return redirect('home')

        messages.error(request, 'Izoh yoki javob matni boʻsh boʻlishi mumkin emas.')
        return redirect('home')

    grouped_histories = defaultdict(list)
    for history in histories:
        grouped_histories[history.userID].append(history)

    context = {
        'users': qs,
        'posts': posts,
        'grouped_histories': grouped_histories.items(),
        'followed_users': followed_ids
    }

    return render(request, 'home.html', context)


@login_required
def post_create(request):
    qs = UserModel.objects.exclude(id=request.user.id).order_by('username')

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
        'users': qs,
        'form': form,
        'user': request.user
    }
    return render(request, 'create.html', context)


class DirectView(TemplateView):
    template_name = 'direct.html'


def explore_view(request):
    posts = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Post).order_by('-created_at')
    reels = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Reels).order_by('-created_at')
    qs = UserModel.objects.exclude(id=request.user.id).order_by('username')

    if request.method == 'POST':
        post_id = request.POST.get('post_id')

        try:
            post = PostModel.objects.get(id=post_id)
        except (PostModel.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'Post not found or invalid ID.')
            return redirect('explore')

        # Comment
        comment_text = request.POST.get('comment')
        if comment_text:
            CommentModel.objects.create(
                postID=post,
                userID=request.user,
                comment=comment_text
            )
            return redirect('explore')

        # Reply
        reply_text = request.POST.get("reply_comment")
        comment_id = request.POST.get('parent_comment_id')
        if reply_text and comment_id:
            try:
                parent_comment = CommentModel.objects.get(id=comment_id)
                ReplyCommentModel.objects.create(
                    postID=parent_comment.postID,
                    reply_comment=reply_text,
                    commentID=parent_comment,
                    userID=request.user,
                )
            except CommentModel.DoesNotExist:
                messages.error(request, 'Parent comment not found.')
            return redirect('explore')

        messages.error(request, 'Comment or reply text cannot be empty')
        return redirect('explore')

    context = {
        'users': qs,
        'posts': posts,
        'reels': reels
    }

    return render(request, 'explore.html', context)


class UserListView(ListView):
    template_name = 'search.html'
    context_object_name = 'users'

    def get_queryset(self):
        qs = UserModel.objects.exclude(id=self.request.user.id)
        q = self.request.GET.get('q')

        if q:
            qs = qs.filter(username__icontains=q)

        return qs


class MessagesView(ListView):
    template_name = 'messages.html'

    context_object_name = 'users'

    def get_queryset(self):
        qs = UserModel.objects.exclude(id=self.request.user.id).order_by('username')
        q = self.request.GET.get('q')

        if q:
            qs = qs.filter(username__icontains=q)

        return qs


class NotificationsView(ListView):
    template_name = 'notifications.html'

    context_object_name = 'users'

    def get_queryset(self):
        qs = UserModel.objects.exclude(id=self.request.user.id).order_by('username')
        q = self.request.GET.get('q')

        if q:
            qs = qs.filter(username__icontains=q)

        return qs


def reels_view(request):
    reels = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Reels).exclude(userID=request.user).order_by('-created_at')
    qs = UserModel.objects.exclude(id=request.user.id).order_by('username')

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
                    postID=parent_comment.postID,
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
        'users': qs,
        'reels': reels,
    }
    return render(request, 'reels.html', context)


def like_create(request, id):
    post = get_object_or_404(PostModel, id=id)

    like = PostLikeModel.objects.filter(postID=post, userID=request.user).first()

    if like:
        like.delete()
    else:
        PostLikeModel.objects.create(postID=post, userID=request.user)

    return redirect(request.GET.get('next', '/'))


@login_required
def like_comment(request, id):
    comment = get_object_or_404(CommentModel, id=id)

    like = CommentLikeModel.objects.filter(commentID=comment, userID=request.user).first()

    if like:
        like.delete()

    else:
        CommentLikeModel.objects.create(commentID=comment, userID=request.user)

    return redirect(request.GET.get('next', '/'))


@login_required
def like_reply_comment(request, id):
    comment = get_object_or_404(ReplyCommentModel, id=id)

    like = ReplyCommentLikeModel.objects.filter(reply_commentID=comment, userID=request.user).first()

    if like:
        like.delete()

    else:
        ReplyCommentLikeModel.objects.create(reply_commentID=comment, userID=request.user)

    return redirect(request.GET.get('next', '/'))


class SavedListView(LoginRequiredMixin, ListView):
    template_name = 'saved.html'
    context_object_name = 'users'

    def get_queryset(self):
        return PostModel.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        qs_users = UserModel.objects.exclude(id=self.request.user.id).order_by('username')
        q = self.request.GET.get('q')

        if q:
            qs_users = qs_users.filter(username__icontains=q)

        context['users'] = qs_users
        context['reels'] = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Reels,
                                                    saved=self.request.user).order_by('-created_at')
        context['posts'] = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Post,
                                                    saved=self.request.user).order_by('-created_at')
        return context


@login_required
def create_saved_video(request, id):
    post = get_object_or_404(PostModel, id=id)

    if request.user in post.saved.all():
        post.saved.remove(request.user)

    else:
        post.saved.add(request.user)

    post.save()

    return redirect(request.GET.get('next', '/'))
