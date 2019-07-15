from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin

from user.models import User
from user.forms import UserForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = ('id', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff')
    list_filter = ('is_superuser', 'is_staff', 'is_active', 'groups')
    search_fields = ('id', 'email', 'first_name', 'last_name')
    filter_horizontal = ('groups', 'user_permissions',)
    list_per_page = 15

    add_form = UserForm
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2',
                       'is_superuser', 'is_staff', 'is_active', 'phone_number', 'groups'),
        }),
    )
    ordering = ('email', )

