from rest_framework import permissions

class IsChannelMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.recipient_channel.members.filter(id=request.user.id).exists()

class CanEditMessage(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user
