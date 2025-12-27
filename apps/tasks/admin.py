from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Task, TaskDependency, TaskComment, SystemCategory, MajorCategory, MinorCategory


@admin.register(SystemCategory)
class SystemCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'project', 'order', 'is_deleted')
    list_filter = ('project', 'is_deleted')
    search_fields = ('code', 'name')
    ordering = ('project', 'order', 'code')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('project', 'code', 'name', 'description', 'order')
        }),
    )


@admin.register(MajorCategory)
class MajorCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'system_category', 'order', 'is_deleted')
    list_filter = ('system_category__project', 'is_deleted')
    search_fields = ('code', 'name')
    ordering = ('system_category', 'order', 'code')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('system_category', 'code', 'name', 'description', 'order')
        }),
    )


@admin.register(MinorCategory)
class MinorCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'major_category', 'order', 'is_deleted')
    list_filter = ('major_category__system_category__project', 'is_deleted')
    search_fields = ('code', 'name')
    ordering = ('major_category', 'order', 'code')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('major_category', 'code', 'name', 'description', 'order')
        }),
    )


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    fields = ['user', 'comment', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Task)
class TaskAdmin(SimpleHistoryAdmin):
    list_display = ['task_number', 'title', 'project', 'system_category', 'major_category', 'minor_category', 'assignee', 'status', 'priority', 'planned_end_date', 'progress_rate']
    list_filter = ['status', 'priority', 'project', 'system_category', 'major_category']
    search_fields = ['task_number', 'title']
    inlines = [TaskCommentInline]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('project', 'system_category', 'major_category', 'minor_category', 'parent', 'task_number', 'title', 'description', 'assignee')
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
