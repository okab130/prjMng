from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Project, ProjectMember, Milestone


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 1
    fields = ['user', 'role', 'left_at']
    readonly_fields = []


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0
    fields = ['name', 'target_date', 'status', 'order']


@admin.register(Project)
class ProjectAdmin(SimpleHistoryAdmin):
    list_display = ['project_code', 'name', 'status', 'start_date', 'end_date', 'progress_rate']
    list_filter = ['status', 'start_date']
    search_fields = ['project_code', 'name']
    inlines = [ProjectMemberInline, MilestoneInline]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('project_code', 'name', 'description', 'status')
        }),
        ('日程', {
            'fields': ('start_date', 'end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('その他', {
            'fields': ('budget', 'progress_rate')
        }),
    )


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'role', 'joined_at']
    list_filter = ['role', 'project']
    search_fields = ['project__name', 'user__display_name']


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'target_date', 'status', 'order']
    list_filter = ['status', 'project']
    search_fields = ['name', 'project__name']
