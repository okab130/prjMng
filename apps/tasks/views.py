from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import redirect
from django.db.models import Q
from apps.projects.models import Project
from apps.accounts.models import User
from .models import Task, TaskComment
from .forms import TaskForm, TaskCommentForm
import json
from datetime import datetime, timedelta


class TaskListView(LoginRequiredMixin, ListView):
    """タスク一覧"""
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Task.objects.select_related('project', 'assignee', 'parent')
        
        # フィルター
        project_id = self.request.GET.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        assignee = self.request.GET.get('assignee')
        if assignee == 'me':
            queryset = queryset.filter(assignee=self.request.user)
        
        return queryset.order_by('planned_end_date')


class TaskDetailView(LoginRequiredMixin, DetailView):
    """タスク詳細"""
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.select_related(
            'project', 'assignee', 'parent'
        ).prefetch_related('comments__user', 'subtasks')


class TaskCreateView(LoginRequiredMixin, CreateView):
    """タスク作成"""
    model = Task
    template_name = 'tasks/task_form.html'
    form_class = TaskForm
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """タスク更新"""
    model = Task
    template_name = 'tasks/task_form.html'
    form_class = TaskForm
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """タスク削除"""
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_deleted = True
        self.object.save()
        return redirect(self.success_url)


class TaskCalendarView(LoginRequiredMixin, TemplateView):
    """タスクカレンダー"""
    template_name = 'tasks/task_calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # フィルター用データ
        context['projects'] = Project.objects.filter(is_deleted=False)
        context['users'] = User.objects.filter(is_active=True)
        context['selected_project'] = self.request.GET.get('project', '')
        context['selected_assignee'] = self.request.GET.get('assignee', '')
        
        # タスクデータ取得
        queryset = Task.objects.filter(is_deleted=False).select_related('project', 'assignee')
        
        # フィルター適用
        project_id = self.request.GET.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        assignee_id = self.request.GET.get('assignee')
        if assignee_id:
            queryset = queryset.filter(assignee_id=assignee_id)
        
        # イベントデータ生成
        events = []
        for task in queryset:
            if task.planned_start_date and task.planned_end_date:
                color = self._get_status_color(task.status)
                events.append({
                    'title': f"{task.task_number} - {task.title}",
                    'start': task.planned_start_date.isoformat(),
                    'end': (task.planned_end_date + timedelta(days=1)).isoformat(),
                    'url': f'/tasks/{task.pk}/',
                    'backgroundColor': color,
                    'borderColor': color,
                    'extendedProps': {
                        'progress': float(task.progress_rate or 0) / 100.0,
                        'status': task.status
                    }
                })
        
        context['events_json'] = json.dumps(events)
        return context
    
    def _get_status_color(self, status):
        colors = {
            'NOT_STARTED': '#6c757d',
            'IN_PROGRESS': '#0d6efd',
            'COMPLETED': '#198754',
            'ON_HOLD': '#ffc107',
            'CANCELLED': '#dc3545'
        }
        return colors.get(status, '#6c757d')


class TaskGanttView(LoginRequiredMixin, TemplateView):
    """ガントチャート"""
    template_name = 'tasks/task_gantt.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # フィルター用データ
        context['projects'] = Project.objects.filter(is_deleted=False)
        context['selected_project'] = self.request.GET.get('project', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['scale'] = self.request.GET.get('scale', 'day')
        
        # タスクデータ取得
        queryset = Task.objects.filter(is_deleted=False).select_related('project', 'assignee', 'parent')
        
        # フィルター適用
        project_id = self.request.GET.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # ガントチャート用データ生成
        tasks_data = []
        for task in queryset:
            if task.planned_start_date and task.planned_end_date:
                duration = (task.planned_end_date - task.planned_start_date).days + 1
                tasks_data.append({
                    'id': task.id,
                    'text': f"{task.task_number} - {task.title}",
                    'start_date': task.planned_start_date.strftime('%Y-%m-%d 00:00'),
                    'duration': duration,
                    'progress': float(task.progress_rate or 0) / 100.0,
                    'parent': task.parent_id if task.parent_id else 0,
                    'status': task.status
                })
        
        context['tasks_json'] = json.dumps(tasks_data)
        return context


class TaskCommentAddView(LoginRequiredMixin, CreateView):
    """タスクコメント追加"""
    model = TaskComment
    template_name = 'tasks/comment_form.html'
    form_class = TaskCommentForm
    
    def form_valid(self, form):
        form.instance.task_id = self.kwargs['task_pk']
        form.instance.user = self.request.user
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.kwargs['task_pk']})
