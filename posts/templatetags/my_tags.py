from django import template
from posts.models import CommentLikeModel

register = template.Library()

@register.simple_tag
def is_comment_liked_by_user(comment, user):
    return CommentLikeModel.objects.filter(commentID=comment, userID=user).exists()
