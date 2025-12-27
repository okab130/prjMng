from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.views import View
from apps.projects.models import Project
from apps.accounts.models import User
from .models import Task, TaskComment, SystemCategory, MajorCategory, MinorCategory
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
        queryset = Task.objects.select_related(
            'project', 'assignee', 'parent',
            'system_category', 'major_category', 'minor_category'
        )
        
        # フィルター
        project_id = self.request.GET.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        system_category_id = self.request.GET.get('system_category')
        if system_category_id:
            queryset = queryset.filter(system_category_id=system_category_id)
        
        major_category_id = self.request.GET.get('major_category')
        if major_category_id:
            queryset = queryset.filter(major_category_id=major_category_id)
        
        minor_category_id = self.request.GET.get('minor_category')
        if minor_category_id:
            queryset = queryset.filter(minor_category_id=minor_category_id)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        assignee = self.request.GET.get('assignee')
        if assignee == 'me':
            queryset = queryset.filter(assignee=self.request.user)
        elif assignee:
            queryset = queryset.filter(assignee_id=assignee)
        
        return queryset.order_by('planned_end_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # フィルター用のマスタデータを取得（DEFAULTを除外）
        context['projects'] = Project.objects.filter(is_deleted=False).order_by('name')
        context['system_categories'] = SystemCategory.objects.filter(
            is_deleted=False
        ).exclude(code='DEFAULT').order_by('order', 'name')
        context['major_categories'] = MajorCategory.objects.filter(
            is_deleted=False
        ).exclude(code='DEFAULT').order_by('order', 'name')
        context['users'] = User.objects.filter(is_active=True).order_by('display_name')
        
        # 選択中の値を保持
        context['selected_project'] = self.request.GET.get('project', '')
        context['selected_system_category'] = self.request.GET.get('system_category', '')
        context['selected_major_category'] = self.request.GET.get('major_category', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_assignee'] = self.request.GET.get('assignee', '')
        
        return context


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


class TaskDuplicateView(LoginRequiredMixin, CreateView):
    """タスク複製"""
    model = Task
    template_name = 'tasks/task_form.html'
    form_class = TaskForm
    
    def get_initial(self):
        """複製元のタスクデータを初期値として設定"""
        original_task = get_object_or_404(Task, pk=self.kwargs['pk'])
        
        return {
            'project': original_task.project,
            'system_category': original_task.system_category,
            'major_category': original_task.major_category,
            'minor_category': original_task.minor_category,
            'parent': original_task.parent,
            'title': f"{original_task.title} (複製)",
            'description': original_task.description,
            'assignee': original_task.assignee,
            'status': Task.StatusChoices.NOT_STARTED,
            'priority': original_task.priority,
            'planned_start_date': original_task.planned_start_date,
            'planned_end_date': original_task.planned_end_date,
            'estimated_hours': original_task.estimated_hours,
            'actual_start_date': None,
            'actual_end_date': None,
            'actual_hours': 0,
            'progress_rate': 0,
        }
    
    def form_valid(self, form):
        # タスク番号は save() で自動生成される
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'タスク「{form.instance.title}」を複製しました。')
        return response
    
    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_duplicate'] = True  # テンプレートで「複製」と表示するため
        original_task = get_object_or_404(Task, pk=self.kwargs['pk'])
        context['original_task'] = original_task
        return context


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
            # 開始日と終了日が両方ある場合のみ表示
            if task.planned_start_date and task.planned_end_date:
                try:
                    duration = (task.planned_end_date - task.planned_start_date).days
                    if duration < 1:
                        duration = 1
                    
                    # dhtmlxGanttが期待する形式: "DD-MM-YYYY" または "YYYY-MM-DD"
                    tasks_data.append({
                        'id': str(task.id),
                        'text': f"{task.task_number} - {task.title}",
                        'start_date': task.planned_start_date.strftime('%Y-%m-%d'),
                        'duration': duration,
                        'progress': float(task.progress_rate or 0) / 100.0,
                        'parent': str(task.parent_id) if task.parent_id else 0,
                        'status': task.status,
                        'open': True
                    })
                except Exception as e:
                    # エラーがあってもスキップして続行
                    continue
        
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


class LoadSystemCategoriesView(LoginRequiredMixin, View):
    """システム名読み込み（Ajax）"""
    
    def get(self, request):
        project_id = request.GET.get('project_id')
        system_categories = SystemCategory.objects.filter(
            project_id=project_id,
            is_deleted=False
        ).order_by('order', 'name').values('id', 'name', 'code')
        
        return JsonResponse(list(system_categories), safe=False)


class LoadMajorCategoriesView(LoginRequiredMixin, View):
    """大分類読み込み（Ajax）"""
    
    def get(self, request):
        system_category_id = request.GET.get('system_category_id')
        major_categories = MajorCategory.objects.filter(
            system_category_id=system_category_id,
            is_deleted=False
        ).order_by('order', 'name').values('id', 'name', 'code')
        
        return JsonResponse(list(major_categories), safe=False)


class LoadMinorCategoriesView(LoginRequiredMixin, View):
    """中分類読み込み（Ajax）"""
    
    def get(self, request):
        major_category_id = request.GET.get('major_category_id')
        minor_categories = MinorCategory.objects.filter(
            major_category_id=major_category_id,
            is_deleted=False
        ).order_by('order', 'name').values('id', 'name', 'code')
        
        return JsonResponse(list(minor_categories), safe=False)
