import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Chat, ChatMessage

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.chat_id = self.scope['url_route']['kwargs']['chat_id']
            self.room_group_name = f"chat_{self.chat_id}"
            
            # Check if user can access the chat
            can_access = await self.can_access_chat()
            if not can_access:
                logger.warning(f"User {self.scope['user']} tried to access unauthorized chat {self.chat_id}")
                await self.close()
                return

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"User {self.scope['user']} connected to chat {self.chat_id}")

        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
                logger.info(f"User {self.scope['user']} disconnected from chat {self.chat_id}")
        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            
            if not message:
                return
            
            # Save message to database
            chat_message = await self.save_message(message)
            if not chat_message:
                return

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message': message,
                    'sender_id': self.scope['user'].id,
                    'timestamp': chat_message.timestamp.isoformat(),
                    'message_id': chat_message.id
                }
            )

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")

    async def chat_message(self, event):
        try:
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'content': event['message'],
                'timestamp': event['timestamp'],
                'is_self': event['sender_id'] == self.scope['user'].id,
                'is_read': False
            }))
            
            # Mark message as read if recipient receives it
            if event['sender_id'] != self.scope['user'].id:
                await self.mark_message_read(event['message_id'])

        except Exception as e:
            logger.error(f"Error in chat_message: {str(e)}")

    @database_sync_to_async
    def can_access_chat(self):
        try:
            user = self.scope['user']
            if not user.is_authenticated:
                return False
            
            chat = Chat.objects.get(id=self.chat_id)
            return chat.participants.filter(id=user.id).exists()
        except Chat.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error checking chat access: {str(e)}")
            return False

    @database_sync_to_async
    def save_message(self, content):
        try:
            user = self.scope['user']
            chat = Chat.objects.get(id=self.chat_id)
            
            if not chat.participants.filter(id=user.id).exists():
                return None
            
            message = ChatMessage.objects.create(
                chat=chat,
                sender=user,
                content=content
            )
            
            # Update chat's last activity
            chat.save()  # This updates the updated_at field
            
            return message
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            return None

    @database_sync_to_async
    def mark_message_read(self, message_id):
        try:
            ChatMessage.objects.filter(id=message_id).update(is_read=True)
        except Exception as e:
            logger.error(f"Error marking message as read: {str(e)}") 