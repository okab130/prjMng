from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Bug, TestCase, TestExecution


class BugListView(LoginRequiredMixin, ListView):
    """バグ一覧"""
    model = Bug
    template_name = 'quality/bug_list.html'
    context_object_name = 'bugs'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Bug.objects.select_related('project', 'assignee', 'reporter')
        
        # フィルター
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('-priority', '-found_date')


class BugDetailView(LoginRequiredMixin, DetailView):
    """バグ詳細"""
    model = Bug
    template_name = 'quality/bug_detail.html'
    context_object_name = 'bug'
    
    def get_queryset(self):
        return Bug.objects.select_related(
            'project', 'assignee', 'reporter', 'related_task'
        ).prefetch_related('comments__user')


class BugCreateView(LoginRequiredMixin, CreateView):
    """バグ作成"""
    model = Bug
    template_name = 'quality/bug_form.html'
    fields = ['project', 'bug_number', 'title', 'description', 'assignee',
              'priority', 'severity', 'category', 'module', 'found_version',
              'reproduction_steps', 'environment']
    
    def form_valid(self, form):
        form.instance.reporter = self.request.user
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('quality:bug_detail', kwargs={'pk': self.object.pk})


class BugUpdateView(LoginRequiredMixin, UpdateView):
    """バグ更新"""
    model = Bug
    template_name = 'quality/bug_form.html'
    fields = ['status', 'assignee', 'priority', 'severity', 'fixed_version',
              'fix_description', 'test_result', 'fixed_date', 'verified_date']
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('quality:bug_detail', kwargs={'pk': self.object.pk})


class BugDeleteView(LoginRequiredMixin, DeleteView):
    """バグ削除"""
    model = Bug
    template_name = 'quality/bug_confirm_delete.html'
    success_url = reverse_lazy('quality:bug_list')


class TestCaseListView(LoginRequiredMixin, ListView):
    """テストケース一覧"""
    model = TestCase
    template_name = 'quality/testcase_list.html'
    context_object_name = 'testcases'
    paginate_by = 50
    
    def get_queryset(self):
        return TestCase.objects.select_related('project').order_by('test_case_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.projects.models import Project
        context['projects'] = Project.objects.all()
        return context


class TestCaseDetailView(LoginRequiredMixin, DetailView):
    """テストケース詳細"""
    model = TestCase
    template_name = 'quality/testcase_detail.html'
    context_object_name = 'testcase'
    
    def get_queryset(self):
        return TestCase.objects.select_related(
            'project', 'related_task'
        ).prefetch_related('executions__executor')


class TestCaseCreateView(LoginRequiredMixin, CreateView):
    """テストケース作成"""
    model = TestCase
    template_name = 'quality/testcase_form.html'
    fields = ['project', 'test_case_number', 'title', 'category', 'priority',
              'precondition', 'test_steps', 'expected_result', 'target_function', 'module']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('quality:testcase_detail', kwargs={'pk': self.object.pk})


class TestCaseUpdateView(LoginRequiredMixin, UpdateView):
    """テストケース更新"""
    model = TestCase
    template_name = 'quality/testcase_form.html'
    fields = ['title', 'category', 'priority', 'precondition', 
              'test_steps', 'expected_result', 'target_function', 'module']
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('quality:testcase_detail', kwargs={'pk': self.object.pk})


class TestExecutionCreateView(LoginRequiredMixin, CreateView):
    """テスト実行"""
    model = TestExecution
    template_name = 'quality/test_execution_form.html'
    fields = ['result', 'actual_result', 'execution_time', 'notes']
    
    def form_valid(self, form):
        form.instance.test_case_id = self.kwargs['testcase_pk']
        form.instance.executor = self.request.user
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('quality:testcase_detail', 
                          kwargs={'pk': self.kwargs['testcase_pk']})


class QualityReportView(LoginRequiredMixin, TemplateView):
    """品質レポート"""
    template_name = 'quality/quality_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # バグ統計
        context['total_bugs'] = Bug.objects.count()
        context['open_bugs'] = Bug.objects.filter(
            status__in=['NEW', 'IN_PROGRESS', 'REOPENED']
        ).count()
        context['fixed_bugs'] = Bug.objects.filter(status='FIXED').count()
        
        # テスト統計
        context['total_testcases'] = TestCase.objects.count()
        context['executed_tests'] = TestExecution.objects.filter(
            result='PASSED'
        ).count()
        
        # 最新バグ一覧
        context['recent_bugs'] = Bug.objects.select_related(
            'project', 'assignee', 'reporter'
        ).order_by('-found_date')[:10]
        
        return context
