from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Review, ReviewParticipant, ReviewIssue


class ReviewParticipantInline(admin.TabularInline):
    model = ReviewParticipant
    extra = 1
    fields = ['user', 'role', 'attended']


class ReviewIssueInline(admin.TabularInline):
    model = ReviewIssue
    extra = 0
    fields = ['issue_number', 'description', 'severity', 'status', 'assignee']


@admin.register(Review)
class ReviewAdmin(SimpleHistoryAdmin):
    list_display = ['review_number', 'title', 'project', 'review_type', 'scheduled_at', 'status', 'conclusion']
    list_filter = ['review_type', 'status', 'conclusion', 'project']
    search_fields = ['review_number', 'title']
    inlines = [ReviewParticipantInline, ReviewIssueInline]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('project', 'review_number', 'title', 'review_type', 'description')
        }),
        ('対象', {
            'fields': ('target_description', 'target_document')
        }),
        ('日時・場所', {
            'fields': ('scheduled_at', 'actual_start_at', 'actual_end_at', 'location')
        }),
        ('ステータス', {
            'fields': ('status', 'conclusion')
        }),
        ('議事録', {
            'fields': ('minutes', 'decisions', 'topics')
        }),
        ('関連', {
            'fields': ('related_task',)
        }),
    )


@admin.register(ReviewParticipant)
class ReviewParticipantAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'role', 'attended']
    list_filter = ['role', 'attended']
    search_fields = ['review__title', 'user__display_name']


@admin.register(ReviewIssue)
class ReviewIssueAdmin(SimpleHistoryAdmin):
    list_display = ['issue_number', 'review', 'severity', 'status', 'reporter', 'assignee']
    list_filter = ['severity', 'status']
    search_fields = ['issue_number', 'description']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('review', 'issue_number', 'description', 'severity', 'status')
        }),
        ('担当', {
            'fields': ('reporter', 'assignee')
        }),
        ('該当箇所', {
            'fields': ('location', 'page_number', 'line_number', 'file_name')
        }),
        ('対応', {
            'fields': ('response', 'resolved_at', 'verifier', 'verified_at')
        }),
    )
