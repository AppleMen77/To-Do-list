from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .models import (
    Workspace, Tag, TodoList, TodoItem, SubTask,
    UserProfile, Achievement, ActivityLog, Comment, Notification, UserRole
)


admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('username', 'email', 'is_staff', 'get_role')
    list_filter = ('is_staff', 'is_superuser', 'role__role')

    def get_role(self, obj):
        role = UserRole.objects.filter(user=obj).first()
        return role.get_role_display() if role else '—'
    get_role.short_description = 'Роль'


@admin.register(UserRole)
class UserRoleAdmin(ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)


@admin.register(Workspace)
class WorkspaceAdmin(ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'color', 'user')
    list_filter = ('user',)


@admin.register(TodoList)
class TodoListAdmin(ModelAdmin):
    list_display = ('name', 'user', 'workspace', 'priority', 'created_at')
    list_filter = ('user', 'workspace', 'priority')
    search_fields = ('name',)


@admin.register(TodoItem)
class TodoItemAdmin(ModelAdmin):
    list_display = ('title', 'user', 'assigned_to', 'completed', 'priority', 'deadline', 'is_pinned', 'is_deleted')
    list_filter = ('completed', 'priority', 'is_pinned', 'is_deleted', 'workspace')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    filter_horizontal = ('tags',)


@admin.register(SubTask)
class SubTaskAdmin(ModelAdmin):
    list_display = ('title', 'todo_item', 'completed')
    list_filter = ('completed',)


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ('user', 'level', 'xp', 'streak', 'last_active_date')
    search_fields = ('user__username',)


@admin.register(Achievement)
class AchievementAdmin(ModelAdmin):
    list_display = ('name', 'description')
    filter_horizontal = ('users',)


@admin.register(ActivityLog)
class ActivityLogAdmin(ModelAdmin):
    list_display = ('user', 'task', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('task__title', 'user__username')
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('user', 'task', 'created_at')
    search_fields = ('text', 'user__username')


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)