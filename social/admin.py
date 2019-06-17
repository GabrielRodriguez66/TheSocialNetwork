from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Personal Information', {'fields': ['username', 'password']}),
        ('Friends', {'fields': ['friends']}),
    ]
    list_display = ('username',)
