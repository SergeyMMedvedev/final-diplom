from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'first_name',
        'last_name',
        'email',
        'password',
        'company',
        'position',
        'type',
    ]
    list_filter = ['first_name']
