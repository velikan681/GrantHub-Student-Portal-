from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Application, Category, Grant, Notification, SavedGrant, User


@admin.register(User)
class PortalUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'full_name', 'role', 'university', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'full_name', 'university')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Профиль', {'fields': ('full_name', 'role', 'university', 'faculty', 'course', 'education_level', 'interests')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'country', 'category', 'opportunity_type', 'deadline', 'created_by')
    list_filter = ('country', 'category', 'opportunity_type', 'education_level')
    search_fields = ('title', 'organization', 'description')
    date_hierarchy = 'deadline'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'grant', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('user__full_name', 'grant__title')


admin.site.register(Category)
admin.site.register(SavedGrant)
admin.site.register(Notification)
