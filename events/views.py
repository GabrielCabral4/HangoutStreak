from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Event, Story, Reaction, Comment, Streak, StoryView, EventPhoto
from .forms import EventForm, EventPhotoForm
from django.http import JsonResponse
from django.db.models import Q, F, Count
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

# Create your views here.

@login_required
def event_list(request):
    """Lista todos os eventos"""
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    past_events = Event.objects.filter(date__lt=timezone.now()).order_by('-date')
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events
    }
    return render(request, 'events/list.html', context)

@login_required
def event_create(request):
    """Cria um novo evento"""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            event.participants.add(request.user)  # Criador automaticamente participa
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('events:detail', event_id=event.id)
    else:
        form = EventForm()
    
    return render(request, 'events/form.html', {'form': form, 'title': 'Criar Evento'})

@login_required
def event_detail(request, event_id):
    """Exibe detalhes de um evento"""
    event = get_object_or_404(Event, id=event_id)
    is_participant = request.user in event.participants.all()
    can_join = not event.is_full and not is_participant
    
    context = {
        'event': event,
        'is_participant': is_participant,
        'can_join': can_join,
        'is_creator': event.creator == request.user
    }
    return render(request, 'events/detail.html', context)

@login_required
def event_edit(request, event_id):
    """Edita um evento existente"""
    event = get_object_or_404(Event, id=event_id)
    
    if event.creator != request.user:
        messages.error(request, 'Você não tem permissão para editar este evento.')
        return redirect('events:detail', event_id=event.id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('events:detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    
    return render(request, 'events/form.html', {'form': form, 'title': 'Editar Evento'})

@login_required
def event_delete(request, event_id):
    """Deleta um evento"""
    event = get_object_or_404(Event, id=event_id)
    
    if event.creator != request.user:
        messages.error(request, 'Você não tem permissão para deletar este evento.')
        return redirect('events:detail', event_id=event.id)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Evento deletado com sucesso!')
        return redirect('events:list')
    
    return render(request, 'events/delete.html', {'event': event})

@login_required
def event_join(request, event_id):
    """Participa de um evento"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.user in event.participants.all():
        messages.warning(request, 'Você já está participando deste evento.')
    elif event.is_full:
        messages.error(request, 'Este evento já está lotado.')
    else:
        event.participants.add(request.user)
        messages.success(request, 'Você está participando do evento!')
    
    return redirect('events:detail', event_id=event.id)

@login_required
def event_leave(request, event_id):
    """Deixa de participar de um evento"""
    event = get_object_or_404(Event, id=event_id)
    
    if event.creator == request.user:
        messages.error(request, 'O criador não pode deixar o evento.')
    elif request.user not in event.participants.all():
        messages.warning(request, 'Você não está participando deste evento.')
    else:
        event.participants.remove(request.user)
        messages.success(request, 'Você deixou o evento.')
    
    return redirect('events:detail', event_id=event.id)

@login_required
def story_feed(request):
    # Get active stories from the last 24 hours
    active_stories = Story.objects.filter(
        expires_at__gt=timezone.now()
    ).select_related('user').prefetch_related(
        'reactions',
        'comments',
        'views'
    ).annotate(
        reaction_count=Count('reactions'),
        comment_count=Count('comments'),
        view_count=Count('views')
    )

    # Get streaks for the current user
    streaks = Streak.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1', 'user2')

    # Format streaks data
    streaks_data = []
    for streak in streaks:
        other_user = streak.user2 if streak.user1 == request.user else streak.user1
        streaks_data.append({
            'other_user': other_user,
            'count': streak.count,
            'is_active': streak.is_active
        })

    return render(request, 'events/story_feed.html', {
        'stories': active_stories,
        'streaks': streaks_data
    })

@login_required
def create_story(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        image = request.FILES.get('image')

        if not text and not image:
            messages.error(request, 'You must provide either text or an image.')
            return redirect('events:story_feed')

        story = Story.objects.create(
            user=request.user,
            text=text,
            image=image
        )

        messages.success(request, 'Story created successfully!')
        return redirect('events:story_feed')

    return render(request, 'events/create_story.html')

@login_required
def view_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    
    # Record the view if not already viewed
    StoryView.objects.get_or_create(user=request.user, story=story)
    
    # Get or create streak between users
    users = sorted([request.user.id, story.user.id])
    streak, created = Streak.objects.get_or_create(
        user1_id=users[0],
        user2_id=users[1],
        defaults={'count': 1}
    )

    # Update streak if it's a new day
    if not created and streak.last_interaction.date() < timezone.now().date():
        streak.increment()

    return render(request, 'events/view_story.html', {
        'story': story,
        'streak': streak
    })

@login_required
def react_to_story(request, story_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    story = get_object_or_404(Story, id=story_id)
    reaction_type = request.POST.get('reaction_type')

    if not reaction_type:
        return JsonResponse({'error': 'Reaction type is required'}, status=400)

    try:
        # Remove existing reaction if any
        Reaction.objects.filter(user=request.user, story=story).delete()
        
        # Create new reaction
        reaction = Reaction.objects.create(
            user=request.user,
            story=story,
            reaction_type=reaction_type
        )

        # Update streak only if not reacting to own story
        if request.user != story.user:
            users = sorted([request.user.id, story.user.id])
            streak, created = Streak.objects.get_or_create(
                user1_id=users[0],
                user2_id=users[1],
                defaults={'count': 1}
            )

            # Update streak if it's a new day
            if not created and streak.last_interaction.date() < timezone.now().date():
                streak.increment()

            streak_count = streak.count
        else:
            streak_count = 0

        return JsonResponse({
            'success': True,
            'reaction_id': reaction.id,
            'streak_count': streak_count
        })

    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def comment_on_story(request, story_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    story = get_object_or_404(Story, id=story_id)
    text = request.POST.get('text')

    if not text:
        return JsonResponse({'error': 'Comment text is required'}, status=400)

    try:
        # Create comment
        comment = Comment.objects.create(
            user=request.user,
            story=story,
            text=text
        )

        # Update streak only if not commenting on own story
        if request.user != story.user:
            users = sorted([request.user.id, story.user.id])
            streak, created = Streak.objects.get_or_create(
                user1_id=users[0],
                user2_id=users[1],
                defaults={'count': 1}
            )

            # Update streak if it's a new day
            if not created and streak.last_interaction.date() < timezone.now().date():
                streak.increment()

            streak_count = streak.count
        else:
            streak_count = 0

        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'streak_count': streak_count
        })

    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def get_streaks(request):
    streaks = Streak.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1', 'user2')

    streaks_data = []
    for streak in streaks:
        other_user = streak.user2 if streak.user1 == request.user else streak.user1
        streaks_data.append({
            'other_user': {
                'username': other_user.username,
                'full_name': other_user.get_full_name(),
            },
            'count': streak.count,
            'is_active': streak.is_active,
            'last_interaction': streak.last_interaction.isoformat()
        })

    return JsonResponse({'streaks': streaks_data})

@login_required
def event_photos(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    photos = event.photos.all()
    
    if request.method == 'POST':
        if request.user not in event.participants.all() and request.user != event.creator:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Apenas participantes podem adicionar fotos.'
                }, status=403)
            messages.error(request, 'Apenas participantes podem adicionar fotos.')
            return redirect('events:detail', event_id=event.id)
            
        form = EventPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                photo = form.save(commit=False)
                photo.event = event
                photo.user = request.user
                photo.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    photo_html = render_to_string('events/partials/photo_card.html', {
                        'photo': photo,
                        'event': event
                    })
                    return JsonResponse({
                        'success': True,
                        'photo_html': photo_html
                    })
                
                messages.success(request, 'Foto adicionada com sucesso!')
                return redirect('events:event_photos', event_id=event.id)
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    }, status=500)
                messages.error(request, f'Erro ao salvar foto: {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Formulário inválido. Verifique os campos.'
                }, status=400)
            messages.error(request, 'Formulário inválido. Verifique os campos.')
    else:
        form = EventPhotoForm()
    
    context = {
        'event': event,
        'photos': photos,
        'form': form
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        photos_html = render_to_string('events/partials/photo_gallery.html', context)
        return JsonResponse({
            'photos_html': photos_html
        })
    
    return render(request, 'events/photos.html', context)

@login_required
def delete_event_photo(request, photo_id):
    photo = get_object_or_404(EventPhoto, id=photo_id)
    event_id = photo.event.id
    
    # Verificar se o usuário é o dono da foto ou o criador do evento
    if request.user != photo.user and request.user != photo.event.creator:
        messages.error(request, 'Você não tem permissão para deletar esta foto.')
        return redirect('events:event_photos', event_id=event_id)
    
    if request.method == 'POST':
        photo.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, 'Foto deletada com sucesso!')
        
    return redirect('events:event_photos', event_id=event_id)
