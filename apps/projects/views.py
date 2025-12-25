from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import Project, ProjectMember, Milestone
from .forms import ProjectForm, MilestoneForm


class ProjectListView(LoginRequiredMixin, ListView):
    """プロジェクト一覧"""
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        return Project.objects.select_related('created_by').prefetch_related('members')


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """プロジェクト詳細"""
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        return Project.objects.select_related('created_by').prefetch_related(
            'members__user', 'milestones', 'tasks', 'bugs'
        )


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """プロジェクト作成"""
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """プロジェクト更新"""
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    """プロジェクト削除"""
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:project_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_deleted = True
        self.object.save()
        return redirect(self.success_url)


class ProjectMemberListView(LoginRequiredMixin, ListView):
    """プロジェクトメンバー一覧"""
    model = ProjectMember
    template_name = 'projects/member_list.html'
    context_object_name = 'members'
    
    def get_queryset(self):
        project_pk = self.kwargs['project_pk']
        return ProjectMember.objects.filter(
            project_id=project_pk
        ).select_related('user', 'project')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return context


class ProjectMemberAddView(LoginRequiredMixin, CreateView):
    """プロジェクトメンバー追加"""
    model = ProjectMember
    template_name = 'projects/member_form.html'
    fields = ['user', 'role']
    
    def form_valid(self, form):
        form.instance.project_id = self.kwargs['project_pk']
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:member_list', 
                          kwargs={'project_pk': self.kwargs['project_pk']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return context


class ProjectMemberRemoveView(LoginRequiredMixin, DeleteView):
    """プロジェクトメンバー削除"""
    model = ProjectMember
    template_name = 'projects/member_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('projects:member_list', 
                          kwargs={'project_pk': self.kwargs['project_pk']})


class MilestoneListView(LoginRequiredMixin, ListView):
    """マイルストーン一覧"""
    model = Milestone
    template_name = 'projects/milestone_list.html'
    context_object_name = 'milestones'
    
    def get_queryset(self):
        project_pk = self.kwargs['project_pk']
        return Milestone.objects.filter(project_id=project_pk).order_by('order', 'target_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return context


class MilestoneCreateView(LoginRequiredMixin, CreateView):
    """マイルストーン作成"""
    model = Milestone
    form_class = MilestoneForm
    template_name = 'projects/milestone_form.html'
    
    def form_valid(self, form):
        form.instance.project_id = self.kwargs['project_pk']
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:milestone_list', 
                          kwargs={'project_pk': self.kwargs['project_pk']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return context


class MilestoneUpdateView(LoginRequiredMixin, UpdateView):
    """マイルストーン更新"""
    model = Milestone
    form_class = MilestoneForm
    template_name = 'projects/milestone_form.html'
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:milestone_list', 
                          kwargs={'project_pk': self.kwargs['project_pk']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return context


class MilestoneDeleteView(LoginRequiredMixin, DeleteView):
    """マイルストーン削除"""
    model = Milestone
    template_name = 'projects/milestone_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('projects:milestone_list', 
                          kwargs={'project_pk': self.kwargs['project_pk']})
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_deleted = True
        self.object.save()
        return super().delete(request, *args, **kwargs)
