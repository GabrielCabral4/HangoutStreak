from django.core.management.base import BaseCommand
from users.models import Achievement

class Command(BaseCommand):
    help = 'Creates initial achievements'

    def handle(self, *args, **kwargs):
        achievements = [
            {
                'name': 'Primeira Estrela',
                'description': 'Mantenha um streak de 15 dias com alguém!',
                'achievement_type': 'streak_15',
                'icon': '⭐'
            },
            {
                'name': 'Segunda Estrela',
                'description': 'Mantenha um streak de 30 dias com alguém!',
                'achievement_type': 'streak_30',
                'icon': '⭐⭐'
            },
            {
                'name': 'Terceira Estrela',
                'description': 'Mantenha um streak de 60 dias com alguém!',
                'achievement_type': 'streak_60',
                'icon': '⭐⭐⭐'
            },
            {
                'name': 'Mestre dos Streaks',
                'description': 'Mantenha um streak incrível de 100 dias!',
                'achievement_type': 'streak_100',
                'icon': '👑'
            },
            {
                'name': 'Organizador Iniciante',
                'description': 'Organize 10 eventos!',
                'achievement_type': 'events_10',
                'icon': '📅'
            },
            {
                'name': 'Organizador Experiente',
                'description': 'Organize 25 eventos!',
                'achievement_type': 'events_25',
                'icon': '🎯'
            },
            {
                'name': 'Mestre dos Eventos',
                'description': 'Organize 50 eventos! Você é incrível!',
                'achievement_type': 'events_50',
                'icon': '🏆'
            },
        ]

        for achievement_data in achievements:
            Achievement.objects.get_or_create(
                achievement_type=achievement_data['achievement_type'],
                defaults={
                    'name': achievement_data['name'],
                    'description': achievement_data['description'],
                    'icon': achievement_data['icon']
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully created achievements')) 