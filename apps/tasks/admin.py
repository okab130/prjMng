from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Task, TaskDependency, TaskComment


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    fields = ['user', 'comment', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Task)
class TaskAdmin(SimpleHistoryAdmin):
    list_display = ['task_number', 'title', 'project', 'assignee', 'status', 'priority', 'planned_end_date', 'progress_rate']
    list_filter = ['status', 'priority', 'project']
    search_fields = ['task_number', 'title']
    inlines = [TaskCommentInline]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('project', 'parent', 'task_number', 'title', 'description', 'assignee')
        }),
        ('ステータス', {
            'fields': ('status', 'priority', 'progress_rate')
        }),
        ('日程', {
            'fields': ('planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('工数', {
            'fields': ('estimated_hours', 'actual_hours')
        }),
        ('WBS', {
            'fields': ('wbs_code', 'level')
        }),
    )


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ['predecessor', 'successor', 'dependency_type', 'lag_days']
    list_filter = ['dependency_type']
    search_fields = ['predecessor__title', 'successor__title']


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['task__title', 'user__display_name', 'comment']
