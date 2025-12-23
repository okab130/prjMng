from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Avg
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.quality.models import Bug, TestCase
from apps.reviews.models import Review
from datetime import datetime, timedelta
from django.utils import timezone
import json


class DashboardView(LoginRequiredMixin, TemplateView):
    """ダッシュボード（拡張版）"""
    template_name = 'dashboard/dashboard_enhanced.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 基本統計
        stats = {}
        stats['total_projects'] = Project.objects.filter(is_deleted=False).count()
        stats['total_tasks'] = Task.objects.filter(is_deleted=False).count()
        stats['in_progress_tasks'] = Task.objects.filter(
            is_deleted=False,
            status=Task.StatusChoices.IN_PROGRESS
        ).count()
        stats['total_bugs'] = Bug.objects.filter(is_deleted=False).count()
        stats['open_bugs'] = Bug.objects.filter(
            is_deleted=False,
            status__in=[Bug.StatusChoices.NEW, Bug.StatusChoices.IN_PROGRESS]
        ).count()
        stats['total_reviews'] = Review.objects.filter(is_deleted=False).count()
        
        # 今月のレビュー数
        now = timezone.now()
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        stats['reviews_this_month'] = Review.objects.filter(
            is_deleted=False,
            scheduled_at__gte=first_day
        ).count()
        
        context['stats'] = stats
        
        # タスクステータス分布
        task_status = Task.objects.filter(is_deleted=False).values('status').annotate(count=Count('id'))
        task_status_labels = []
        task_status_data = []
        for item in task_status:
            task_status_labels.append(dict(Task.StatusChoices.choices).get(item['status']))
            task_status_data.append(item['count'])
        context['task_status_data'] = json.dumps({
            'labels': task_status_labels,
            'data': task_status_data
        })
        
        # バグ重要度分布
        bug_severity = Bug.objects.filter(is_deleted=False).values('severity').annotate(count=Count('id'))
        bug_severity_labels = []
        bug_severity_data = []
        for item in bug_severity:
            bug_severity_labels.append(dict(Bug.SeverityChoices.choices).get(item['severity']))
            bug_severity_data.append(item['count'])
        context['bug_severity_data'] = json.dumps({
            'labels': bug_severity_labels,
            'data': bug_severity_data
        })
        
        # プロジェクト進捗
        projects = Project.objects.filter(is_deleted=False)[:5]
        project_labels = [p.name for p in projects]
        project_data = [p.progress_rate if p.progress_rate else 0 for p in projects]
        context['project_progress_data'] = json.dumps({
            'labels': project_labels,
            'data': project_data
        })
        
        # 月別タスク完了数（過去6ヶ月）
        completion_labels = []
        completion_data = []
        for i in range(5, -1, -1):
            month_start = (now - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i > 0:
                month_end = (now - timedelta(days=30*(i-1))).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                month_end = now
            
            count = Task.objects.filter(
                is_deleted=False,
                status=Task.StatusChoices.COMPLETED,
                actual_end_date__gte=month_start,
                actual_end_date__lt=month_end
            ).count()
            
            completion_labels.append(month_start.strftime('%Y/%m'))
            completion_data.append(count)
        
        context['task_completion_data'] = json.dumps({
            'labels': completion_labels,
            'data': completion_data
        })
        
        # 最近のタスク
        context['recent_tasks'] = Task.objects.filter(
            is_deleted=False
        ).select_related('project').order_by('-updated_at')[:5]
        
        # 最近のバグ
        context['recent_bugs'] = Bug.objects.filter(
            is_deleted=False
        ).select_related('project').order_by('-created_at')[:5]
        
        return context
