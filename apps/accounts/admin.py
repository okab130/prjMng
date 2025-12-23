from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, SimpleHistoryAdmin):
    list_display = ['username', 'employee_id', 'display_name', 'role', 'department', 'is_active']
    list_filter = ['role', 'is_active', 'department']
    search_fields = ['username', 'employee_id', 'display_name', 'email']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('追加情報', {
            'fields': ('employee_id', 'display_name', 'department', 'role', 'phone', 'avatar', 'last_login_at')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('追加情報', {
            'fields': ('employee_id', 'display_name', 'department', 'role', 'phone')
        }),
    )
