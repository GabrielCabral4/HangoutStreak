from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Event(models.Model):
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição')
    date = models.DateTimeField('Data')
    location = models.CharField('Local', max_length=200)
    max_participants = models.IntegerField('Máximo de Participantes')
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_events'
    )
    participants = models.ManyToManyField(
        User,
        related_name='participating_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='event_pics/', null=True, blank=True)
    is_private = models.BooleanField('Evento Privado', default=False)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Update creator's total events count
            self.creator.profile.total_events += 1
            self.creator.profile.save()
            
            # Check for achievements
            self.creator.profile.check_and_award_achievements()

    class Meta:
        ordering = ['date']
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return self.title

    @property
    def is_past(self):
        return self.date < timezone.now()

    @property
    def is_upcoming(self):
        return self.date >= timezone.now()

    @property
    def is_full(self):
        return self.participants.count() >= self.max_participants


class EventMessage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'

    def __str__(self):
        return f'{self.user.username} - {self.timestamp}'

class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='stories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"Story by {self.user.username} at {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Stories'

class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('haha', '😂'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😠'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'story']
        ordering = ['-created_at']

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_comments')
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

class Streak(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streaks_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streaks_as_user2')
    count = models.IntegerField(default=1)
    last_interaction = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user1', 'user2']
        ordering = ['-count']

    def __str__(self):
        return f"Streak between {self.user1.username} and {self.user2.username} ({self.count} days)"

    @property
    def is_active(self):
        return (timezone.now() - self.last_interaction) < timedelta(hours=24)

    def increment(self):
        self.count += 1
        self.save()
        
        # Update streak count for both users
        self.user1.profile.streak_count = self.count
        self.user2.profile.streak_count = self.count
        
        # Check for achievements
        self.user1.profile.check_and_award_achievements()
        self.user2.profile.check_and_award_achievements()
        
        # Save profiles
        self.user1.profile.save()
        self.user2.profile.save()

    def reset(self):
        self.count = 0
        self.save()
        
        # Reset streak count for both users
        self.user1.profile.streak_count = 0
        self.user2.profile.streak_count = 0
        self.user1.profile.save()
        self.user2.profile.save()

class StoryView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_views')
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'story']
        ordering = ['-viewed_at']

class EventPhoto(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='photos')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_photos')
    image = models.ImageField(upload_to='event_photos/')
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Foto do Evento'
        verbose_name_plural = 'Fotos do Evento'

    def __str__(self):
        return f"Foto de {self.user.username} no evento {self.event.title}"
