from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Bug, BugComment, TestCase, TestExecution, QualityMetric


class BugCommentInline(admin.TabularInline):
    model = BugComment
    extra = 0
    fields = ['user', 'comment', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Bug)
class BugAdmin(SimpleHistoryAdmin):
    list_display = ['bug_number', 'title', 'project', 'status', 'priority', 'severity', 'assignee', 'found_date']
    list_filter = ['status', 'priority', 'severity', 'project']
    search_fields = ['bug_number', 'title']
    inlines = [BugCommentInline]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('project', 'bug_number', 'title', 'description')
        }),
        ('担当', {
            'fields': ('reporter', 'assignee')
        }),
        ('ステータス', {
            'fields': ('status', 'priority', 'severity')
        }),
        ('分類', {
            'fields': ('category', 'module', 'found_version', 'fixed_version')
        }),
        ('詳細', {
            'fields': ('reproduction_steps', 'environment', 'fix_description', 'test_result')
        }),
        ('日程', {
            'fields': ('found_date', 'fixed_date', 'verified_date')
        }),
        ('関連', {
            'fields': ('related_task',)
        }),
    )


@admin.register(BugComment)
class BugCommentAdmin(admin.ModelAdmin):
    list_display = ['bug', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['bug__title', 'user__display_name', 'comment']


class TestExecutionInline(admin.TabularInline):
    model = TestExecution
    extra = 0
    fields = ['executor', 'executed_at', 'result', 'execution_time']
    readonly_fields = ['executed_at']


@admin.register(TestCase)
class TestCaseAdmin(SimpleHistoryAdmin):
    list_display = ['test_case_number', 'title', 'project', 'category', 'priority']
    list_filter = ['category', 'priority', 'project']
    search_fields = ['test_case_number', 'title']
    inlines = [TestExecutionInline]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('project', 'test_case_number', 'title', 'category', 'priority')
        }),
        ('テスト内容', {
            'fields': ('precondition', 'test_steps', 'expected_result')
        }),
        ('分類', {
            'fields': ('target_function', 'module')
        }),
        ('関連', {
            'fields': ('related_task',)
        }),
    )


@admin.register(TestExecution)
class TestExecutionAdmin(admin.ModelAdmin):
    list_display = ['test_case', 'executor', 'executed_at', 'result', 'execution_time']
    list_filter = ['result', 'executed_at']
    search_fields = ['test_case__title', 'executor__display_name']


@admin.register(QualityMetric)
class QualityMetricAdmin(admin.ModelAdmin):
    list_display = ['project', 'metric_name', 'metric_type', 'target_value', 'actual_value', 'measured_at']
    list_filter = ['metric_type', 'measured_at', 'project']
    search_fields = ['metric_name', 'project__name']
