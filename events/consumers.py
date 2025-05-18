import json
import logging
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from .models import Event, EventMessage

logger = logging.getLogger(__name__)

class EventChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.event_id = self.scope['url_route']['kwargs']['event_id']
            self.room_group_name = str(self.event_id)  # Simplified group name
            logger.info(f"Attempting to connect to chat {self.room_group_name}")

            # Check if user can join the chat
            can_access = await self.can_access_chat()
            logger.info(f"Can access chat: {can_access}")
            
            if not can_access:
                logger.warning("Access denied to chat")
                await self.close()
                return

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"Added to group {self.room_group_name}")

            await self.accept()
            logger.info(f"WebSocket connection accepted for user {self.scope['user']} in event {self.event_id}")

        except Exception as e:
            logger.error(f"Error in connect: {e}\n{traceback.format_exc()}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
                logger.info(f"Left group {self.room_group_name} with code {close_code}")
        except Exception as e:
            logger.error(f"Error in disconnect: {e}\n{traceback.format_exc()}")

    async def receive(self, text_data):
        try:
            if not text_data:
                logger.warning("Received empty text_data")
                return

            data = json.loads(text_data)
            if 'message' not in data:
                logger.warning("Received data without message field")
                return

            message = data['message'].strip()
            if not message:
                logger.warning("Received empty message")
                return

            user = self.scope['user']
            if not user.is_authenticated:
                logger.warning(f"Unauthenticated user tried to send message")
                return

            # Save message to database
            saved_message = await self.save_message(user, message)
            if not saved_message:
                logger.error("Failed to save message to database")
                return

            # Get user avatar URL using sync_to_async
            user_avatar = await self.get_user_avatar(user)

            # Prepare message data
            message_data = {
                'type': 'chat.message',
                'message': message,
                'username': user.username,
                'user_avatar': user_avatar,
                'timestamp': timezone.now().isoformat()
            }

            # Send message to room group
            logger.info(f"Sending message to group {self.room_group_name}: {message_data}")
            await self.channel_layer.group_send(
                self.room_group_name,
                message_data
            )

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}\n{text_data}")
        except Exception as e:
            logger.error(f"Error in receive: {e}\n{traceback.format_exc()}")

    async def chat_message(self, event):
        try:
            # Remove type from event before sending to WebSocket
            message_data = event.copy()
            message_data.pop('type')
            
            logger.info(f"Sending message to WebSocket: {message_data}")
            await self.send(text_data=json.dumps(message_data))
            logger.info("Message successfully sent to WebSocket")
        except Exception as e:
            logger.error(f"Error in chat_message: {e}\n{traceback.format_exc()}")

    @database_sync_to_async
    def get_user_avatar(self, user):
        """Get user avatar URL in a sync context"""
        try:
            if hasattr(user, 'profile') and user.profile.avatar:
                return user.profile.avatar.url
            return None
        except Exception as e:
            logger.error(f"Error getting user avatar: {e}")
            return None

    @database_sync_to_async
    def can_access_chat(self):
        try:
            user = self.scope['user']
            if not user.is_authenticated:
                return False

            event = Event.objects.get(id=self.event_id)
            return user in event.participants.all() or user == event.creator
        except Event.DoesNotExist:
            logger.error(f"Event {self.event_id} does not exist")
            return False
        except Exception as e:
            logger.error(f"Error checking access: {e}")
            return False

    @database_sync_to_async
    def save_message(self, user, message):
        try:
            event = Event.objects.get(id=self.event_id)
            if user in event.participants.all() or user == event.creator:
                return EventMessage.objects.create(
                    event=event,
                    user=user,
                    content=message
                )
            logger.warning(f"User {user} tried to save message but is not a participant")
            return None
        except Event.DoesNotExist:
            logger.error(f"Event {self.event_id} does not exist when saving message")
            return None
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None 