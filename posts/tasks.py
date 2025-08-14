from django.utils import timezone
from datetime import timedelta

from celery import shared_task

from posts.models import PostModel


@shared_task
def check_stories_status():
    one_day_ago = timezone.now() - timedelta(days=1)

    base_history_filters = {
        'post_type': PostModel.PostTypeChoice.History,
        'created_at__gte': one_day_ago
    }
    stories = PostModel.objects.filter(**base_history_filters)

    for story in stories:
        story.archived = True
        story.save()
