from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from events.models import Event
from django.utils import timezone

def home(request):
    """Página inicial do site"""
    context = {
        'is_home': True
    }
    
    if request.user.is_authenticated:
        # Buscar próximos eventos do usuário
        upcoming_events = Event.objects.filter(
            participants=request.user,
            date__gte=timezone.now()
        ).order_by('date')[:3]
        
        context.update({
            'upcoming_events': upcoming_events
        })
    
    return render(request, 'core/home.html', context)
