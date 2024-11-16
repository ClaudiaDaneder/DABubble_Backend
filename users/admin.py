from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'last_name', 'first_name', 'email', 'is_active',)
    list_filter = ('is_active', 'email', 'last_name', 'first_name',)
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        ('Personal Information', {'fields': ('first_name', 'last_name',)}),
        ('Avatar', {'fields': ('image_url',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active',)}
        ),
    )
    search_fields = ('email', 'last_name', 'first_name',)
    ordering = ('id',)

admin.site.register(CustomUser, CustomUserAdmin)