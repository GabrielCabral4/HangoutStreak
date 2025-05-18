from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os

class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('streak_15', 'Primeira Estrela (15 dias de Streak)'),
        ('streak_30', 'Segunda Estrela (30 dias de Streak)'),
        ('streak_60', 'Terceira Estrela (60 dias de Streak)'),
        ('streak_100', 'Mestre dos Streaks (100 dias)'),
        ('events_10', 'Organizador Iniciante (10 eventos)'),
        ('events_25', 'Organizador Experiente (25 eventos)'),
        ('events_50', 'Mestre dos Eventos (50 eventos)'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = models.CharField(max_length=20)  # Emoji or icon class
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['achievement_type']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    friends = models.ManyToManyField('self', blank=True)
    streak_count = models.IntegerField('Streak Atual', default=0)
    total_events = models.IntegerField('Total de Eventos', default=0)
    achievements = models.ManyToManyField(Achievement, blank=True, related_name='users')
    highest_streak = models.IntegerField('Maior Streak', default=0)
    
    def __str__(self):
        return f'{self.user.username} Profile'
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.avatar:
            img = Image.open(self.avatar.path)
            
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)

    def check_and_award_achievements(self):
        # Check streak-based achievements
        streak_achievements = {
            15: 'streak_15',
            30: 'streak_30',
            60: 'streak_60',
            100: 'streak_100'
        }

        # Update highest streak if current streak is higher
        if self.streak_count > self.highest_streak:
            self.highest_streak = self.streak_count
            self.save()

        # Check and award streak achievements
        for streak_days, achievement_type in streak_achievements.items():
            if self.highest_streak >= streak_days:
                achievement = Achievement.objects.get(achievement_type=achievement_type)
                self.achievements.add(achievement)

        # Check event-based achievements
        event_achievements = {
            10: 'events_10',
            25: 'events_25',
            50: 'events_50'
        }

        # Check and award event achievements
        for event_count, achievement_type in event_achievements.items():
            if self.total_events >= event_count:
                achievement = Achievement.objects.get(achievement_type=achievement_type)
                self.achievements.add(achievement)
