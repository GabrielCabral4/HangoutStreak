from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_other_participant(self, current_user):
        """Returns the other participant in a two-person chat"""
        # If participants are prefetched, use them
        if hasattr(self, '_prefetched_objects_cache') and 'participants' in self._prefetched_objects_cache:
            return next((p for p in self.participants.all() if p.id != current_user.id), None)
        return self.participants.exclude(id=current_user.id).first()

    def get_last_message(self):
        """Returns the last message in the chat"""
        # If messages are prefetched, use them
        if hasattr(self, 'latest_messages') and self.latest_messages:
            return self.latest_messages[0]
        return self.messages.order_by('-timestamp').first()

    def __str__(self):
        participants = ", ".join([user.username for user in self.participants.all()])
        return f"Chat between {participants}"

    class Meta:
        ordering = ['-updated_at']

class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.content

    class Meta:
        ordering = ['timestamp']
