from django.contrib import admin
from django.contrib.admin import ModelAdmin
from chat.models import Channel, Message

class MessageAdmin(ModelAdmin):
    model = Message
    list_display = ('id', 'sender', 'recipient_type', 'recipient_channel', 'recipient_user', 'content',)

admin.site.register(Channel)
admin.site.register(Message, MessageAdmin)
