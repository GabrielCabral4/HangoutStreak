from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q, Max, Count, Exists, OuterRef, Prefetch
from django.core.paginator import Paginator
from .models import Chat, ChatMessage

# Create your views here.

@login_required
def chat_rooms(request):
    return render(request, 'chat/rooms.html')

@login_required
def chat_room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })

@login_required
def inbox(request):
    # Get all chats for the current user with their last message and participants
    chats = Chat.objects.filter(participants=request.user)\
        .prefetch_related(
            'participants',
            Prefetch(
                'messages',
                queryset=ChatMessage.objects.order_by('-timestamp'),
                to_attr='latest_messages'
            )
        )\
        .annotate(
            unread_count=Count(
                'messages',
                filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
            )
        ).order_by('-updated_at')

    # Pre-calculate other participants and last messages
    chat_data = []
    for chat in chats:
        other_participant = next((p for p in chat.participants.all() if p.id != request.user.id), None)
        last_message = chat.latest_messages[0] if chat.latest_messages else None
        chat_data.append({
            'chat': chat,
            'other_user': other_participant,
            'last_message': last_message,
            'unread_count': chat.unread_count
        })

    return render(request, 'chat/inbox.html', {
        'chat_data': chat_data
    })

@login_required
def new_chat(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            other_user = get_object_or_404(User, id=user_id)
            
            # Check if a chat already exists between these users
            existing_chat = Chat.objects.filter(
                participants=request.user
            ).filter(
                participants=other_user
            ).first()
            
            if existing_chat:
                return redirect('chat:detail', chat_id=existing_chat.id)
            
            # Create new chat
            chat = Chat.objects.create()
            chat.participants.add(request.user, other_user)
            return redirect('chat:detail', chat_id=chat.id)
    
    return render(request, 'chat/new_chat.html')

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    other_user = chat.get_other_participant(request.user)
    
    # Mark messages as read
    ChatMessage.objects.filter(
        chat=chat,
        is_read=False
    ).exclude(
        sender=request.user
    ).update(is_read=True)
    
    return render(request, 'chat/detail.html', {
        'chat': chat,
        'other_user': other_user
    })

@login_required
def load_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    page = request.GET.get('page', 1)
    
    messages = chat.messages.select_related('sender').order_by('-timestamp')
    paginator = Paginator(messages, 50)
    page_obj = paginator.get_page(page)
    
    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'sender': msg.sender.username,
        'timestamp': msg.timestamp.isoformat(),
        'is_read': msg.is_read,
        'is_self': msg.sender == request.user
    } for msg in page_obj]
    
    return JsonResponse({
        'messages': messages_data,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None
    })

@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    # Search for users excluding the current user
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(
        id=request.user.id
    ).values('id', 'username', 'first_name', 'last_name')[:10]
    
    return JsonResponse({'users': list(users)})
