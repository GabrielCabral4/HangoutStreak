from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Story, Streak

@shared_task
def check_and_update_streaks():
    """
    Check and update streaks based on story activity.
    This task should run daily.
    """
    # Get all active streaks
    active_streaks = Streak.objects.filter(count__gt=0)

    for streak in active_streaks:
        # Check if either user has posted a story in the last 24 hours
        user1_has_story = Story.objects.filter(
            user=streak.user1,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).exists()

        user2_has_story = Story.objects.filter(
            user=streak.user2,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).exists()

        # If either user hasn't posted in 24 hours, reset the streak
        if not user1_has_story or not user2_has_story:
            streak.reset()

@shared_task
def cleanup_expired_stories():
    """
    Delete stories that have expired (older than 24 hours).
    This task should run hourly.
    """
    Story.objects.filter(expires_at__lte=timezone.now()).delete() 