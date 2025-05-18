from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Event, EventPhoto
from .serializers import EventSerializer, EventPhotoSerializer
from django.shortcuts import get_object_or_404

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        event = serializer.save(creator=self.request.user)
        event.participants.add(self.request.user)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        event = self.get_object()
        if request.user in event.participants.all():
            return Response(
                {'detail': 'Você já está participando deste evento.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if event.is_full:
            return Response(
                {'detail': 'Este evento está lotado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        event.participants.add(request.user)
        return Response({'detail': 'Você está participando do evento!'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        event = self.get_object()
        if event.creator == request.user:
            return Response(
                {'detail': 'O criador não pode deixar o evento.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user not in event.participants.all():
            return Response(
                {'detail': 'Você não está participando deste evento.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        event.participants.remove(request.user)
        return Response({'detail': 'Você deixou o evento.'})

class EventPhotoViewSet(viewsets.ModelViewSet):
    queryset = EventPhoto.objects.all()
    serializer_class = EventPhotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return EventPhoto.objects.filter(event_id=self.kwargs['event_pk'])

    def perform_create(self, serializer):
        event = get_object_or_404(Event, pk=self.kwargs['event_pk'])
        if self.request.user not in event.participants.all() and self.request.user != event.creator:
            raise permissions.PermissionDenied('Apenas participantes podem adicionar fotos.')
        serializer.save(event=event, user=self.request.user) 