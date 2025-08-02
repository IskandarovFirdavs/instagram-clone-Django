import json

from django.db import IntegrityError
from django.db.models import Count, Prefetch
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView, ListView
from posts.forms import PostModelForm
from posts.models import PostModel, PostLikeModel, CommentModel, CommentLikeModel, ReplyCommentModel, \
    ReplyCommentLikeModel, NotificationModel
from collections import defaultdict

from users.models import UserModel, Follow


@login_required(login_url='login')
def home_view(request):
    followed_users = request.user.following_set.all()
    followed_ids = [followed.following.id for followed in followed_users]
    one_month_ago = timezone.now() - timedelta(days=3)
    one_day_ago = timezone.now() - timedelta(days=77)
    qs = UserModel.objects.exclude(id=request.user.id)

    base_post_filters = {
        'post_type': PostModel.PostTypeChoice.Post,
        'created_at__gte': one_month_ago
    }

    base_history_filters = {
        'post_type': PostModel.PostTypeChoice.History,
        'created_at__gte': one_day_ago
    }

    if len(followed_ids) > 3:
        base_post_filters['userID__in'] = followed_ids
        base_history_filters['userID__in'] = followed_ids

    posts = PostModel.objects.filter(
        **base_post_filters
    ).prefetch_related(
        Prefetch(
            'comments',
            queryset=CommentModel.objects.annotate(
                likes_count=Count('comment_likes')
            ).prefetch_related(
                Prefetch(
                    'reply_comments',
                    queryset=ReplyCommentModel.objects.annotate(
                        likes_count=Count('reply_comment_likes')
                    )
                )
            )
        ),
        'likes',
        'saved'
    ).order_by('-created_at').exclude(userID=request.user)

    histories = PostModel.objects.filter(
        **base_history_filters
    ).prefetch_related(
        'likes',
        'saved'
    ).order_by('-created_at')

    grouped_histories = defaultdict(list)
    for history in histories:
        grouped_histories[history.userID].append(history)

    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        comment_text = request.POST.get('comment')
        reply_text = request.POST.get('reply_comment')
        comment_id = request.POST.get('parent_comment_id')

        if comment_text and post_id:
            try:
                post = PostModel.objects.get(id=post_id)
                CommentModel.objects.create(
                    postID=post,
                    userID=request.user,
                    comment=comment_text
                )
                messages.success(request, 'Comment added successfully!')
                return redirect(f"{request.path}?show_comments={post_id}#post-{post_id}")
            except PostModel.DoesNotExist:
                messages.error(request, 'Post not found.')
                return redirect(request.path)

        if reply_text and comment_id:
            try:
                parent_comment = CommentModel.objects.get(id=comment_id)
                ReplyCommentModel.objects.create(
                    postID=parent_comment.postID,
                    reply_comment=reply_text,
                    commentID=parent_comment,
                    userID=request.user,
                )
                messages.success(request, 'Reply added successfully!')
                return redirect(
                    f"{request.path}?show_comments={parent_comment.postID.id}&show_replies={comment_id}#post-{parent_comment.postID.id}")
            except CommentModel.DoesNotExist:
                messages.error(request, 'Comment not found.')
                return redirect(request.path)

        messages.error(request, 'Comment or reply text cannot be empty.')
        return redirect(request.path)
    context = {
        'posts': posts,
        'users': qs,
        'grouped_histories': grouped_histories.items(),
        'followed_users': followed_ids,
        'show_comments': request.GET.get('show_comments'),
        'show_replies': request.GET.get('show_replies'),
        'reply_to': request.GET.get('reply_to')
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


@login_required(login_url='login')
def explore_view(request):
    posts = PostModel.objects.filter(
        post_type=PostModel.PostTypeChoice.Post
    ).prefetch_related(
        Prefetch(
            'comments',
            queryset=CommentModel.objects.annotate(
                likes_count=Count('comment_likes')
            ).prefetch_related(
                Prefetch(
                    'reply_comments',
                    queryset=ReplyCommentModel.objects.annotate(
                        likes_count=Count('reply_comment_likes')
                    )
                )
            )
        ),
        'likes',
        'saved',
    ).order_by('-created_at')

    reels = PostModel.objects.filter(
        post_type=PostModel.PostTypeChoice.Reels
    ).prefetch_related(
        Prefetch(
            'comments',
            queryset=CommentModel.objects.annotate(
                likes_count=Count('comment_likes')
            ).prefetch_related(
                Prefetch(
                    'reply_comments',
                    queryset=ReplyCommentModel.objects.annotate(
                        likes_count=Count('reply_comment_likes')
                    )
                )
            )
        ),
        'likes',
        'saved',
    ).order_by('-created_at')

    qs = UserModel.objects.exclude(id=request.user.id).order_by('username')

    if request.method == 'POST':
        post_id = request.POST.get('post_id')

        try:
            post = PostModel.objects.get(id=post_id)
        except (PostModel.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'Post not found or invalid ID.')
            return redirect('explore')

        comment_text = request.POST.get('comment')
        if comment_text:
            CommentModel.objects.create(
                postID=post,
                userID=request.user,
                comment=comment_text
            )
            return redirect('explore')

        reply_text = request.POST.get('reply_comment')
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
        'reels': reels,
        'open_post_id': request.GET.get('post_id')
    }
    return render(request, 'explore.html', context)


@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(CommentModel, id=comment_id)
    action = request.GET.get('action')
    next_url = request.GET.get('next', '/explore/')
    post_id = request.GET.get('post_id')

    like_qs = CommentLikeModel.objects.filter(commentID=comment, userID=request.user)
    if action == 'like' and not like_qs.exists():
        CommentLikeModel.objects.create(commentID=comment, userID=request.user)
    elif action == 'unlike' and like_qs.exists():
        like_qs.delete()

    if post_id:
        next_url += f'?post_id={post_id}'
    return redirect(next_url)


from django.db import IntegrityError

from django.db import IntegrityError
from django.http import HttpResponseBadRequest

@login_required
def home_comment_like(request, comment_id):
    comment = get_object_or_404(CommentModel, id=comment_id)
    user = request.user
    like = CommentLikeModel.objects.filter(commentID=comment, userID=user).first()

    comment_owner = comment.userID
    is_self_like = (comment_owner == user)

    if like:
        like.delete()
        if not is_self_like:
            NotificationModel.objects.filter(
                comment_like=comment,
                liked_by=user
            ).delete()
    else:
        CommentLikeModel.objects.create(commentID=comment, userID=request.user)
        if not is_self_like:
            if comment_owner and comment_owner.pk:
                try:
                    obj, created = NotificationModel.objects.get_or_create(
                        comment_like=comment,
                        liked_by=user,
                        owner=comment_owner,
                        post_like=None,
                        reply_comment_like=None
                    )
                    print("Notification created:", created)
                except IntegrityError as e:
                    print("❌ Notification creation failed:", str(e))
            else:
                print("⚠️ Skipped: Comment owner is invalid")

    return redirect(request.GET.get('next', '/'))



@login_required
def home_reply_comment_like(request, id):
    reply_comment = get_object_or_404(ReplyCommentModel, id=id)


    like = ReplyCommentLikeModel.objects.filter(reply_commentID=reply_comment, userID=request.user).first()
    if like:
        like.delete()
    else:
        ReplyCommentLikeModel.objects.create(reply_commentID=reply_comment, userID=request.user)

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


def followers_list_view(request):
    users = UserModel.objects.filter(request.user.following_set)

    return


def followings_list_view(request):
    users = UserModel.objects.filter(request.user.following_set)
    return


class MessagesView(ListView):
    template_name = 'messages.html'

    context_object_name = 'users'

    def get_queryset(self):
        qs = UserModel.objects.exclude(id=self.request.user.id).order_by('username')
        q = self.request.GET.get('q')

        if q:
            qs = qs.filter(username__icontains=q)

        return qs


def reels_view(request):
    reels = PostModel.objects.filter(post_type=PostModel.PostTypeChoice.Reels).exclude(userID=request.user).order_by(
        '-created_at')
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


@login_required
def like_create(request, id):
    post = get_object_or_404(PostModel, id=id)
    like = PostLikeModel.objects.filter(postID=post, userID=request.user).first()

    if like:
        like.delete()
        liked = False
    else:
        PostLikeModel.objects.create(postID=post, userID=request.user)
        liked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': post.likes_count()
        })
    return redirect(request.GET.get('next', '/'))


@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(CommentModel, id=comment_id)
    action = request.GET.get('action')
    next_url = request.GET.get('next', '/explore/')

    like_qs = CommentLikeModel.objects.filter(commentID=comment, userID=request.user)

    if action == 'like' and not like_qs.exists():
        CommentLikeModel.objects.create(commentID=comment, userID=request.user)
    elif action == 'unlike' and like_qs.exists():
        like_qs.delete()

    return redirect(next_url)


@login_required
def like_reply_comment(request, id):
    reply = get_object_or_404(ReplyCommentModel, id=id)
    action = request.GET.get('action')
    next_url = request.GET.get('next', '/explore/')
    post_id = request.GET.get('post_id')

    like_qs = ReplyCommentLikeModel.objects.filter(reply_commentID=reply, userID=request.user)

    if action == 'like' and not like_qs.exists():
        ReplyCommentLikeModel.objects.create(reply_commentID=reply, userID=request.user)
    elif action == 'unlike' and like_qs.exists():
        like_qs.delete()

    if post_id:
        next_url += f'?post_id={post_id}'
    return redirect(next_url)


def reply_comment_like_view(request, id):
    reply = get_object_or_404(ReplyCommentModel, id=id)
    user = request.user
    if user.is_authenticated:
        if user in reply.likes.all():
            reply.likes.remove(user)
        else:
            reply.likes.add(user)
    next_url = request.GET.get('next', 'home')
    return redirect(next_url)


def create_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(PostModel, id=post_id)
        comment_text = request.POST.get('comment')
        if comment_text and request.user.is_authenticated:
            CommentModel.objects.create(userID=request.user, postID=post, comment=comment_text)
        next_url = request.POST.get('next', 'home')
        return redirect(next_url)
    return redirect('home')


def create_reply_comment(request, parent_comment_id):
    if request.method == 'POST':
        parent_comment = get_object_or_404(CommentModel, id=parent_comment_id)
        reply_text = request.POST.get('reply_comment')
        if reply_text and request.user.is_authenticated:
            ReplyCommentModel.objects.create(
                userID=request.user,
                commentID=parent_comment,
                reply_comment=reply_text
            )

        next_url = request.POST.get('next', 'home')
        return redirect(next_url)
    return redirect('home')


@login_required
def notification_view(request):
    notifications = NotificationModel.objects.filter(owner=request.user).exclude(liked_by=request.user).order_by(
        '-created_at')

    context = {
        'notifications': notifications
    }

    return render(request, 'notifications.html', context)
