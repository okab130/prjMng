# 機能概要・URL設計・ビュー設計書

## 1. アプリケーション構成

### 1.1 Djangoアプリケーション構造
```
prjmng/                          # プロジェクトルート
├── manage.py
├── requirements.txt
├── config/                      # プロジェクト設定
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py             # 共通設定
│   │   ├── development.py      # 開発環境
│   │   └── production.py       # 本番環境
│   ├── urls.py                 # ルートURL設定
│   ├── wsgi.py
│   └── asgi.py
├── apps/                        # アプリケーション群
│   ├── accounts/               # ユーザー管理
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── projects/               # プロジェクト管理
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── tasks/                  # スケジュール管理
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── quality/                # 品質管理（バグ・テスト）
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── reviews/                # レビュー管理
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── dashboard/              # ダッシュボード
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   └── notifications/          # 通知（Phase 2）
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       └── templates/
├── static/                      # 静的ファイル
│   ├── css/
│   ├── js/
│   └── images/
├── media/                       # アップロードファイル
└── templates/                   # 共通テンプレート
    ├── base.html
    ├── includes/
    └── errors/
```

---

## 2. URL設計

### 2.1 URLルーティング全体構成

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 管理画面
    path('admin/', admin.site.urls),
    
    # 認証
    path('accounts/', include('apps.accounts.urls')),
    
    # ダッシュボード
    path('', include('apps.dashboard.urls')),
    
    # プロジェクト管理
    path('projects/', include('apps.projects.urls')),
    
    # スケジュール管理
    path('tasks/', include('apps.tasks.urls')),
    
    # 品質管理
    path('quality/', include('apps.quality.urls')),
    
    # レビュー管理
    path('reviews/', include('apps.reviews.urls')),
    
    # 通知（Phase 2）
    path('notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

### 2.2 accounts（ユーザー管理）URL設計

| URL | Name | View | 機能 | Method |
|-----|------|------|------|--------|
| `/accounts/login/` | login | LoginView | ログイン | GET, POST |
| `/accounts/logout/` | logout | LogoutView | ログアウト | POST |
| `/accounts/profile/` | profile | ProfileView | プロフィール表示 | GET |
| `/accounts/profile/edit/` | profile_edit | ProfileEditView | プロフィール編集 | GET, POST |
| `/accounts/password/change/` | password_change | PasswordChangeView | パスワード変更 | GET, POST |
| `/accounts/users/` | user_list | UserListView | ユーザー一覧（管理者） | GET |
| `/accounts/users/create/` | user_create | UserCreateView | ユーザー作成（管理者） | GET, POST |
| `/accounts/users/<int:pk>/` | user_detail | UserDetailView | ユーザー詳細 | GET |
| `/accounts/users/<int:pk>/edit/` | user_edit | UserEditView | ユーザー編集（管理者） | GET, POST |
| `/accounts/users/<int:pk>/delete/` | user_delete | UserDeleteView | ユーザー削除（管理者） | POST |

```python
# apps/accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
]
```

---

### 2.3 dashboard（ダッシュボード）URL設計

| URL | Name | View | 機能 | Method |
|-----|------|------|------|--------|
| `/` | dashboard | DashboardView | 総合ダッシュボード | GET |
| `/dashboard/my-tasks/` | my_tasks | MyTasksView | 自分のタスク一覧 | GET |
| `/dashboard/my-bugs/` | my_bugs | MyBugsView | 自分のバグ一覧 | GET |
| `/dashboard/my-reviews/` | my_reviews | MyReviewsView | 自分のレビュー一覧 | GET |

```python
# apps/dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/my-tasks/', views.MyTasksView.as_view(), name='my_tasks'),
    path('dashboard/my-bugs/', views.MyBugsView.as_view(), name='my_bugs'),
    path('dashboard/my-reviews/', views.MyReviewsView.as_view(), name='my_reviews'),
]
```

---

### 2.4 projects（プロジェクト管理）URL設計

| URL | Name | View | 機能 | Method |
|-----|------|------|------|--------|
| `/projects/` | project_list | ProjectListView | プロジェクト一覧 | GET |
| `/projects/create/` | project_create | ProjectCreateView | プロジェクト作成 | GET, POST |
| `/projects/<int:pk>/` | project_detail | ProjectDetailView | プロジェクト詳細 | GET |
| `/projects/<int:pk>/edit/` | project_edit | ProjectEditView | プロジェクト編集 | GET, POST |
| `/projects/<int:pk>/delete/` | project_delete | ProjectDeleteView | プロジェクト削除 | POST |
| `/projects/<int:pk>/members/` | project_members | ProjectMembersView | メンバー管理 | GET |
| `/projects/<int:pk>/members/add/` | member_add | MemberAddView | メンバー追加 | GET, POST |
| `/projects/<int:pk>/members/<int:member_id>/edit/` | member_edit | MemberEditView | メンバー役割変更 | GET, POST |
| `/projects/<int:pk>/members/<int:member_id>/remove/` | member_remove | MemberRemoveView | メンバー削除 | POST |
| `/projects/<int:pk>/milestones/` | milestone_list | MilestoneListView | マイルストーン一覧 | GET |
| `/projects/<int:pk>/milestones/create/` | milestone_create | MilestoneCreateView | マイルストーン作成 | GET, POST |
| `/projects/<int:pk>/milestones/<int:ms_pk>/edit/` | milestone_edit | MilestoneEditView | マイルストーン編集 | GET, POST |
| `/projects/<int:pk>/milestones/<int:ms_pk>/delete/` | milestone_delete | MilestoneDeleteView | マイルストーン削除 | POST |

```python
# apps/projects/urls.py
from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/edit/', views.ProjectEditView.as_view(), name='project_edit'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('<int:pk>/members/', views.ProjectMembersView.as_view(), name='project_members'),
    path('<int:pk>/members/add/', views.MemberAddView.as_view(), name='member_add'),
    path('<int:pk>/members/<int:member_id>/edit/', views.MemberEditView.as_view(), name='member_edit'),
    path('<int:pk>/members/<int:member_id>/remove/', views.MemberRemoveView.as_view(), name='member_remove'),
    path('<int:pk>/milestones/', views.MilestoneListView.as_view(), name='milestone_list'),
    path('<int:pk>/milestones/create/', views.MilestoneCreateView.as_view(), name='milestone_create'),
    path('<int:pk>/milestones/<int:ms_pk>/edit/', views.MilestoneEditView.as_view(), name='milestone_edit'),
    path('<int:pk>/milestones/<int:ms_pk>/delete/', views.MilestoneDeleteView.as_view(), name='milestone_delete'),
]
```

---

### 2.5 tasks（スケジュール管理）URL設計

| URL | Name | View | 機能 | Method |
|-----|------|------|------|--------|
| `/tasks/` | task_list | TaskListView | タスク一覧（全体） | GET |
| `/tasks/project/<int:project_pk>/` | task_list_by_project | TaskListByProjectView | プロジェクト別タスク一覧 | GET |
| `/tasks/create/` | task_create | TaskCreateView | タスク作成 | GET, POST |
| `/tasks/<int:pk>/` | task_detail | TaskDetailView | タスク詳細 | GET |
| `/tasks/<int:pk>/edit/` | task_edit | TaskEditView | タスク編集 | GET, POST |
| `/tasks/<int:pk>/delete/` | task_delete | TaskDeleteView | タスク削除 | POST |
| `/tasks/<int:pk>/comments/` | task_comments | TaskCommentsView | コメント一覧・追加 | GET, POST |
| `/tasks/gantt/<int:project_pk>/` | gantt_chart | GanttChartView | ガントチャート | GET |
| `/tasks/calendar/` | calendar | CalendarView | カレンダー | GET |
| `/tasks/calendar/<int:year>/<int:month>/` | calendar_month | CalendarMonthView | 月次カレンダー | GET |
| `/tasks/<int:pk>/dependencies/` | task_dependencies | TaskDependenciesView | 依存関係管理 | GET, POST |
| `/tasks/<int:pk>/dependencies/<int:dep_pk>/delete/` | dependency_delete | DependencyDeleteView | 依存関係削除 | POST |

```python
# apps/tasks/urls.py
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.TaskListView.as_view(), name='task_list'),
    path('project/<int:project_pk>/', views.TaskListByProjectView.as_view(), name='task_list_by_project'),
    path('create/', views.TaskCreateView.as_view(), name='task_create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('<int:pk>/edit/', views.TaskEditView.as_view(), name='task_edit'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('<int:pk>/comments/', views.TaskCommentsView.as_view(), name='task_comments'),
    path('gantt/<int:project_pk>/', views.GanttChartView.as_view(), name='gantt_chart'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.CalendarMonthView.as_view(), name='calendar_month'),
    path('<int:pk>/dependencies/', views.TaskDependenciesView.as_view(), name='task_dependencies'),
    path('<int:pk>/dependencies/<int:dep_pk>/delete/', views.DependencyDeleteView.as_view(), name='dependency_delete'),
]
```

---

### 2.6 quality（品質管理）URL設計

| URL | Name | View | 機能 | Method |
|-----|------|------|------|--------|
| `/quality/dashboard/<int:project_pk>/` | quality_dashboard | QualityDashboardView | 品質ダッシュボード | GET |
| `/quality/bugs/` | bug_list | BugListView | バグ一覧（全体） | GET |
| `/quality/bugs/project/<int:project_pk>/` | bug_list_by_project | BugListByProjectView | プロジェクト別バグ一覧 | GET |
| `/quality/bugs/create/` | bug_create | BugCreateView | バグ作成 | GET, POST |
| `/quality/bugs/<int:pk>/` | bug_detail | BugDetailView | バグ詳細 | GET |
| `/quality/bugs/<int:pk>/edit/` | bug_edit | BugEditView | バグ編集 | GET, POST |
| `/quality/bugs/<int:pk>/delete/` | bug_delete | BugDeleteView | バグ削除 | POST |
| `/quality/bugs/<int:pk>/comments/` | bug_comments | BugCommentsView | コメント一覧・追加 | GET, POST |
| `/quality/bugs/report/<int:project_pk>/` | bug_report | BugReportView | バグレポート | GET |
| `/quality/testcases/` | testcase_list | TestCaseListView | テストケース一覧 | GET |
| `/quality/testcases/project/<int:project_pk>/` | testcase_list_by_project | TestCaseListByProjectView | プロジェクト別一覧 | GET |
| `/quality/testcases/create/` | testcase_create | TestCaseCreateView | テストケース作成 | GET, POST |
| `/quality/testcases/<int:pk>/` | testcase_detail | TestCaseDetailView | テストケース詳細 | GET |
| `/quality/testcases/<int:pk>/edit/` | testcase_edit | TestCaseEditView | テストケース編集 | GET, POST |
| `/quality/testcases/<int:pk>/delete/` | testcase_delete | TestCaseDeleteView | テストケース削除 | POST |
| `/quality/testcases/<int:pk>/execute/` | testcase_execute | TestCaseExecuteView | テスト実行 | GET, POST |
| `/quality/executions/<int:project_pk>/` | execution_list | ExecutionListView | テスト実行履歴 | GET |
| `/quality/metrics/<int:project_pk>/` | metrics_list | MetricsListView | 品質メトリクス | GET |
| `/quality/metrics/<int:project_pk>/add/` | metrics_add | MetricsAddView | メトリクス追加 | GET, POST |

```python
# apps/quality/urls.py
from django.urls import path
from . import views

app_name = 'quality'

urlpatterns = [
    path('dashboard/<int:project_pk>/', views.QualityDashboardView.as_view(), name='quality_dashboard'),
    # バグ管理
    path('bugs/', views.BugListView.as_view(), name='bug_list'),
    path('bugs/project/<int:project_pk>/', views.BugListByProjectView.as_view(), name='bug_list_by_project'),
    path('bugs/create/', views.BugCreateView.as_view(), name='bug_create'),
    path('bugs/<int:pk>/', views.BugDetailView.as_view(), name='bug_detail'),
    path('bugs/<int:pk>/edit/', views.BugEditView.as_view(), name='bug_edit'),
    path('bugs/<int:pk>/delete/', views.BugDeleteView.as_view(), name='bug_delete'),
    path('bugs/<int:pk>/comments/', views.BugCommentsView.as_view(), name='bug_comments'),
    path('bugs/report/<int:project_pk>/', views.BugReportView.as_view(), name='bug_report'),
    # テストケース管理
    path('testcases/', views.TestCaseListView.as_view(), name='testcase_list'),
    path('testcases/project/<int:project_pk>/', views.TestCaseListByProjectView.as_view(), name='testcase_list_by_project'),
    path('testcases/create/', views.TestCaseCreateView.as_view(), name='testcase_create'),
    path('testcases/<int:pk>/', views.TestCaseDetailView.as_view(), name='testcase_detail'),
    path('testcases/<int:pk>/edit/', views.TestCaseEditView.as_view(), name='testcase_edit'),
    path('testcases/<int:pk>/delete/', views.TestCaseDeleteView.as_view(), name='testcase_delete'),
    path('testcases/<int:pk>/execute/', views.TestCaseExecuteView.as_view(), name='testcase_execute'),
    # テスト実行・メトリクス
    path('executions/<int:project_pk>/', views.ExecutionListView.as_view(), name='execution_list'),
    path('metrics/<int:project_pk>/', views.MetricsListView.as_view(), name='metrics_list'),
    path('metrics/<int:project_pk>/add/', views.MetricsAddView.as_view(), name='metrics_add'),
]
```

---

### 2.7 reviews（レビュー管理）URL設計

| URL | Name | View | 機能 | Method |
|-----|------|------|------|--------|
| `/reviews/` | review_list | ReviewListView | レビュー一覧（全体） | GET |
| `/reviews/project/<int:project_pk>/` | review_list_by_project | ReviewListByProjectView | プロジェクト別一覧 | GET |
| `/reviews/create/` | review_create | ReviewCreateView | レビュー作成 | GET, POST |
| `/reviews/<int:pk>/` | review_detail | ReviewDetailView | レビュー詳細 | GET |
| `/reviews/<int:pk>/edit/` | review_edit | ReviewEditView | レビュー編集 | GET, POST |
| `/reviews/<int:pk>/delete/` | review_delete | ReviewDeleteView | レビュー削除 | POST |
| `/reviews/<int:pk>/participants/` | review_participants | ReviewParticipantsView | 参加者管理 | GET, POST |
| `/reviews/<int:pk>/issues/` | review_issues | ReviewIssuesView | 指摘事項一覧 | GET |
| `/reviews/<int:pk>/issues/create/` | issue_create | IssueCreateView | 指摘事項作成 | GET, POST |
| `/reviews/<int:pk>/issues/<int:issue_pk>/` | issue_detail | IssueDetailView | 指摘事項詳細 | GET |
| `/reviews/<int:pk>/issues/<int:issue_pk>/edit/` | issue_edit | IssueEditView | 指摘事項編集 | GET, POST |
| `/reviews/<int:pk>/issues/<int:issue_pk>/delete/` | issue_delete | IssueDeleteView | 指摘事項削除 | POST |
| `/reviews/<int:pk>/complete/` | review_complete | ReviewCompleteView | レビュー完了 | POST |
| `/reviews/report/<int:project_pk>/` | review_report | ReviewReportView | レビューレポート | GET |

```python
# apps/reviews/urls.py
from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.ReviewListView.as_view(), name='review_list'),
    path('project/<int:project_pk>/', views.ReviewListByProjectView.as_view(), name='review_list_by_project'),
    path('create/', views.ReviewCreateView.as_view(), name='review_create'),
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),
    path('<int:pk>/edit/', views.ReviewEditView.as_view(), name='review_edit'),
    path('<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    path('<int:pk>/participants/', views.ReviewParticipantsView.as_view(), name='review_participants'),
    path('<int:pk>/issues/', views.ReviewIssuesView.as_view(), name='review_issues'),
    path('<int:pk>/issues/create/', views.IssueCreateView.as_view(), name='issue_create'),
    path('<int:pk>/issues/<int:issue_pk>/', views.IssueDetailView.as_view(), name='issue_detail'),
    path('<int:pk>/issues/<int:issue_pk>/edit/', views.IssueEditView.as_view(), name='issue_edit'),
    path('<int:pk>/issues/<int:issue_pk>/delete/', views.IssueDeleteView.as_view(), name='issue_delete'),
    path('<int:pk>/complete/', views.ReviewCompleteView.as_view(), name='review_complete'),
    path('report/<int:project_pk>/', views.ReviewReportView.as_view(), name='review_report'),
]
```

---

## 3. ビュー設計

### 3.1 ビュー設計方針

- **クラスベースビュー（CBV）を優先使用**
  - Django標準のジェネリックビュー活用
  - ListView, DetailView, CreateView, UpdateView, DeleteView
- **Mixinパターンで共通処理を実装**
  - LoginRequiredMixin: 認証必須
  - PermissionRequiredMixin: 権限チェック（Phase 2）
  - ProjectContextMixin: プロジェクトコンテキスト注入
- **トランザクション管理**
  - @transaction.atomicデコレーターで整合性保証

---

### 3.2 共通Mixin

```python
# apps/core/mixins.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from apps.projects.models import Project, ProjectMember

class ProjectContextMixin:
    """プロジェクトコンテキストを追加するMixin"""
    def get_project(self):
        project_pk = self.kwargs.get('project_pk') or self.kwargs.get('pk')
        return get_object_or_404(Project, pk=project_pk, is_deleted=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'project'):
            context['project'] = self.project
        return context

class ProjectMemberRequiredMixin:
    """プロジェクトメンバーであることを確認するMixin（Phase 2で詳細実装）"""
    def dispatch(self, request, *args, **kwargs):
        # Phase 1では全ユーザーがアクセス可能
        return super().dispatch(request, *args, **kwargs)
```

---

### 3.3 主要ビューの実装例

#### 3.3.1 ダッシュボード

```python
# apps/dashboard/views.py

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.quality.models import Bug
from apps.reviews.models import Review

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 参加プロジェクト
        context['my_projects'] = Project.objects.filter(
            members__user=user,
            is_deleted=False
        ).select_related().annotate(
            task_count=Count('tasks', filter=Q(tasks__is_deleted=False)),
            bug_count=Count('bugs', filter=Q(bugs__is_deleted=False))
        )[:5]
        
        # 自分のタスク（期限が近い順）
        context['my_tasks'] = Task.objects.filter(
            assignee=user,
            status__in=['NOT_STARTED', 'IN_PROGRESS'],
            is_deleted=False
        ).select_related('project').order_by('planned_end_date')[:10]
        
        # 自分のバグ
        context['my_bugs'] = Bug.objects.filter(
            assignee=user,
            status__in=['NEW', 'IN_PROGRESS'],
            is_deleted=False
        ).select_related('project').order_by('-priority', '-found_date')[:10]
        
        # 自分のレビュー
        context['my_reviews'] = Review.objects.filter(
            participants__user=user,
            status__in=['PLANNED', 'IN_PROGRESS'],
            is_deleted=False
        ).select_related('project').order_by('scheduled_at')[:10]
        
        return context
```

#### 3.3.2 プロジェクト管理

```python
# apps/projects/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db import transaction
from .models import Project, ProjectMember, Milestone
from .forms import ProjectForm, ProjectMemberForm, MilestoneForm

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Project.objects.filter(is_deleted=False)
        
        # 検索フィルター
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(project_code__icontains=search)
            )
        
        return queryset.order_by('-created_at')

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        return Project.objects.filter(is_deleted=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        
        # プロジェクト統計
        context['stats'] = {
            'total_tasks': project.tasks.filter(is_deleted=False).count(),
            'completed_tasks': project.tasks.filter(status='COMPLETED', is_deleted=False).count(),
            'total_bugs': project.bugs.filter(is_deleted=False).count(),
            'open_bugs': project.bugs.filter(status__in=['NEW', 'IN_PROGRESS'], is_deleted=False).count(),
            'total_reviews': project.reviews.filter(is_deleted=False).count(),
        }
        
        # メンバー一覧
        context['members'] = project.members.filter(
            is_deleted=False
        ).select_related('user').order_by('role', 'user__display_name')
        
        # 最近のアクティビティ（Phase 2）
        
        return context

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    
    @transaction.atomic
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # 作成者を自動的にPMとして追加
        ProjectMember.objects.create(
            project=self.object,
            user=self.request.user,
            role='PM',
            created_by=self.request.user
        )
        
        return response
    
    def get_success_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.object.pk})

class ProjectEditView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    
    def get_queryset(self):
        return Project.objects.filter(is_deleted=False)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.object.pk})
```

#### 3.3.3 タスク管理

```python
# apps/tasks/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Prefetch
from .models import Task, TaskDependency, TaskComment
from .forms import TaskForm, TaskCommentForm

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Task.objects.filter(is_deleted=False).select_related(
            'project', 'assignee', 'parent'
        )
        
        # フィルター
        project_pk = self.request.GET.get('project')
        if project_pk:
            queryset = queryset.filter(project_id=project_pk)
        
        assignee = self.request.GET.get('assignee')
        if assignee:
            queryset = queryset.filter(assignee_id=assignee)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('planned_end_date')

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(is_deleted=False).select_related(
            'project', 'assignee', 'parent'
        ).prefetch_related(
            'subtasks',
            'comments__user',
            'predecessors__predecessor',
            'successors__successor'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = TaskCommentForm()
        return context

class GanttChartView(LoginRequiredMixin, TemplateView):
    template_name = 'tasks/gantt_chart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs.get('project_pk')
        
        context['project'] = get_object_or_404(Project, pk=project_pk, is_deleted=False)
        context['tasks'] = Task.objects.filter(
            project_id=project_pk,
            is_deleted=False
        ).select_related('assignee').prefetch_related(
            'predecessors__predecessor',
            'successors__successor'
        ).order_by('wbs_code', 'planned_start_date')
        
        # ガントチャート用のJSONデータ生成（JavaScript側で描画）
        
        return context
```

#### 3.3.4 品質管理（バグ管理）

```python
# apps/quality/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db.models import Count, Q
from .models import Bug, BugComment, TestCase, TestExecution
from .forms import BugForm, BugCommentForm, TestCaseForm, TestExecutionForm

class QualityDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'quality/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs.get('project_pk')
        project = get_object_or_404(Project, pk=project_pk, is_deleted=False)
        
        context['project'] = project
        
        # バグ統計
        bugs = Bug.objects.filter(project=project, is_deleted=False)
        context['bug_stats'] = {
            'total': bugs.count(),
            'open': bugs.filter(status__in=['NEW', 'IN_PROGRESS', 'REOPENED']).count(),
            'fixed': bugs.filter(status='FIXED').count(),
            'verified': bugs.filter(status='VERIFIED').count(),
            'critical': bugs.filter(priority='CRITICAL').count(),
        }
        
        # バグトレンド（直近30日）
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        context['recent_bugs'] = bugs.filter(
            found_date__gte=thirty_days_ago
        ).order_by('-found_date')
        
        # テスト統計
        test_cases = TestCase.objects.filter(project=project, is_deleted=False)
        context['test_stats'] = {
            'total': test_cases.count(),
            'executed': TestExecution.objects.filter(
                test_case__project=project,
                result='PASSED'
            ).values('test_case').distinct().count(),
        }
        
        return context

class BugListView(LoginRequiredMixin, ListView):
    model = Bug
    template_name = 'quality/bug_list.html'
    context_object_name = 'bugs'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Bug.objects.filter(is_deleted=False).select_related(
            'project', 'reporter', 'assignee'
        )
        
        # フィルター処理
        project_pk = self.request.GET.get('project')
        if project_pk:
            queryset = queryset.filter(project_id=project_pk)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        assignee = self.request.GET.get('assignee')
        if assignee:
            queryset = queryset.filter(assignee_id=assignee)
        
        return queryset.order_by('-found_date', '-priority')
```

#### 3.3.5 レビュー管理

```python
# apps/reviews/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db import transaction
from django.shortcuts import redirect
from .models import Review, ReviewParticipant, ReviewIssue
from .forms import ReviewForm, ReviewIssueForm
from apps.notifications.models import Notification

class ReviewDetailView(LoginRequiredMixin, DetailView):
    model = Review
    template_name = 'reviews/review_detail.html'
    context_object_name = 'review'
    
    def get_queryset(self):
        return Review.objects.filter(is_deleted=False).select_related(
            'project'
        ).prefetch_related(
            'participants__user',
            'issues__reporter',
            'issues__assignee'
        )

class ReviewCompleteView(LoginRequiredMixin, View):
    """レビュー完了処理"""
    
    @transaction.atomic
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk, is_deleted=False)
        
        # レビューを完了状態に変更
        review.status = 'COMPLETED'
        review.actual_end_at = timezone.now()
        review.updated_by = request.user
        review.save()
        
        # PMに通知
        Notification.notify_project_managers(
            project=review.project,
            notification_type='REVIEW_COMPLETED',
            title=f'レビュー完了: {review.title}',
            message=f'{review.title}が完了しました。',
            content_object=review
        )
        
        messages.success(request, 'レビューを完了しました。')
        return redirect('reviews:review_detail', pk=pk)
```

---

## 4. 画面一覧と機能詳細

### 4.1 共通画面

| 画面ID | 画面名 | URL | 主要機能 |
|--------|--------|-----|----------|
| C-01 | ログイン画面 | `/accounts/login/` | ユーザー認証 |
| C-02 | ダッシュボード | `/` | 総合情報表示、自分のタスク・バグ・レビュー |
| C-03 | プロフィール表示 | `/accounts/profile/` | ユーザー情報表示 |
| C-04 | プロフィール編集 | `/accounts/profile/edit/` | 表示名、メール、電話、アバター編集 |

### 4.2 プロジェクト管理画面

| 画面ID | 画面名 | URL | 主要機能 |
|--------|--------|-----|----------|
| P-01 | プロジェクト一覧 | `/projects/` | 一覧表示、検索、フィルター |
| P-02 | プロジェクト詳細 | `/projects/<pk>/` | 詳細情報、統計、メンバー一覧 |
| P-03 | プロジェクト作成 | `/projects/create/` | 新規作成 |
| P-04 | プロジェクト編集 | `/projects/<pk>/edit/` | 情報編集 |
| P-05 | メンバー管理 | `/projects/<pk>/members/` | メンバー追加・削除・役割変更 |
| P-06 | マイルストーン管理 | `/projects/<pk>/milestones/` | マイルストーン一覧・作成・編集 |

### 4.3 スケジュール管理画面

| 画面ID | 画面名 | URL | 主要機能 |
|--------|--------|-----|----------|
| T-01 | タスク一覧 | `/tasks/` | 一覧表示、フィルター、検索 |
| T-02 | タスク詳細 | `/tasks/<pk>/` | 詳細情報、コメント、履歴 |
| T-03 | タスク作成 | `/tasks/create/` | 新規作成 |
| T-04 | タスク編集 | `/tasks/<pk>/edit/` | 情報編集 |
| T-05 | ガントチャート | `/tasks/gantt/<project_pk>/` | ガントチャート表示、依存関係可視化 |
| T-06 | カレンダー | `/tasks/calendar/` | 月次・週次カレンダー表示 |
| T-07 | 依存関係管理 | `/tasks/<pk>/dependencies/` | 依存関係の追加・削除 |

### 4.4 品質管理画面

| 画面ID | 画面名 | URL | 主要機能 |
|--------|--------|-----|----------|
| Q-01 | 品質ダッシュボード | `/quality/dashboard/<project_pk>/` | バグ統計、テスト進捗、トレンド |
| Q-02 | バグ一覧 | `/quality/bugs/` | 一覧表示、フィルター |
| Q-03 | バグ詳細 | `/quality/bugs/<pk>/` | 詳細情報、コメント、履歴 |
| Q-04 | バグ登録 | `/quality/bugs/create/` | 新規登録 |
| Q-05 | バグ編集 | `/quality/bugs/<pk>/edit/` | 情報編集 |
| Q-06 | バグレポート | `/quality/bugs/report/<project_pk>/` | バグレポート生成・出力 |
| Q-07 | テストケース一覧 | `/quality/testcases/` | 一覧表示 |
| Q-08 | テストケース詳細 | `/quality/testcases/<pk>/` | 詳細情報、実行履歴 |
| Q-09 | テスト実行 | `/quality/testcases/<pk>/execute/` | テスト実行結果登録 |
| Q-10 | 品質メトリクス | `/quality/metrics/<project_pk>/` | メトリクス一覧・グラフ表示 |

### 4.5 レビュー管理画面

| 画面ID | 画面名 | URL | 主要機能 |
|--------|--------|-----|----------|
| R-01 | レビュー一覧 | `/reviews/` | 一覧表示、フィルター |
| R-02 | レビュー詳細 | `/reviews/<pk>/` | 詳細情報、参加者、指摘事項 |
| R-03 | レビュー作成 | `/reviews/create/` | 新規作成 |
| R-04 | レビュー編集 | `/reviews/<pk>/edit/` | 情報編集 |
| R-05 | 参加者管理 | `/reviews/<pk>/participants/` | 参加者追加・削除 |
| R-06 | 指摘事項一覧 | `/reviews/<pk>/issues/` | 指摘事項一覧表示 |
| R-07 | 指摘事項詳細 | `/reviews/<pk>/issues/<issue_pk>/` | 詳細情報、対応状況 |
| R-08 | 指摘事項登録 | `/reviews/<pk>/issues/create/` | 新規登録 |
| R-09 | レビューレポート | `/reviews/report/<project_pk>/` | レビューレポート生成 |

### 4.6 管理画面

| 画面ID | 画面名 | URL | 主要機能 |
|--------|--------|-----|----------|
| A-01 | ユーザー管理 | `/accounts/users/` | ユーザー一覧・作成・編集・削除（管理者） |
| A-02 | Django Admin | `/admin/` | システム管理（管理者） |

---

## 5. フォーム設計

### 5.1 主要フォームクラス

```python
# apps/projects/forms.py
from django import forms
from .models import Project, ProjectMember, Milestone

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_code', 'name', 'description', 'status', 
                  'start_date', 'end_date', 'budget']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

# apps/tasks/forms.py
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'parent', 'task_number', 'title', 'description',
                  'assignee', 'status', 'priority', 'planned_start_date',
                  'planned_end_date', 'estimated_hours', 'progress_rate']
        widgets = {
            'planned_start_date': forms.DateInput(attrs={'type': 'date'}),
            'planned_end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

# apps/quality/forms.py
class BugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ['project', 'title', 'description', 'assignee', 'priority',
                  'severity', 'category', 'module', 'reproduction_steps',
                  'environment', 'found_version']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'reproduction_steps': forms.Textarea(attrs={'rows': 4}),
            'environment': forms.Textarea(attrs={'rows': 3}),
        }
```

---

## 6. テンプレート設計

### 6.1 テンプレート構成

```
templates/
├── base.html                    # ベーステンプレート
├── includes/
│   ├── header.html             # ヘッダー（ナビゲーション）
│   ├── footer.html             # フッター
│   ├── messages.html           # フラッシュメッセージ
│   ├── pagination.html         # ページネーション
│   └── breadcrumb.html         # パンくずリスト
├── dashboard/
│   └── dashboard.html          # ダッシュボード
├── projects/
│   ├── project_list.html       # プロジェクト一覧
│   ├── project_detail.html     # プロジェクト詳細
│   └── project_form.html       # プロジェクト作成・編集
├── tasks/
│   ├── task_list.html          # タスク一覧
│   ├── task_detail.html        # タスク詳細
│   ├── task_form.html          # タスク作成・編集
│   ├── gantt_chart.html        # ガントチャート
│   └── calendar.html           # カレンダー
├── quality/
│   ├── dashboard.html          # 品質ダッシュボード
│   ├── bug_list.html           # バグ一覧
│   ├── bug_detail.html         # バグ詳細
│   └── bug_form.html           # バグ作成・編集
└── reviews/
    ├── review_list.html        # レビュー一覧
    ├── review_detail.html      # レビュー詳細
    └── review_form.html        # レビュー作成・編集
```

### 6.2 ベーステンプレート例

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}プロジェクト管理システム{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'includes/header.html' %}
    
    <main class="container-fluid">
        <div class="row">
            <!-- サイドバー -->
            <nav class="col-md-2 d-md-block bg-light sidebar">
                {% block sidebar %}
                <div class="position-sticky pt-3">
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'dashboard:dashboard' %}">
                                ダッシュボード
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'projects:project_list' %}">
                                プロジェクト
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'tasks:task_list' %}">
                                タスク
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'quality:bug_list' %}">
                                バグ
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'reviews:review_list' %}">
                                レビュー
                            </a>
                        </li>
                    </ul>
                </div>
                {% endblock %}
            </nav>
            
            <!-- メインコンテンツ -->
            <main class="col-md-10 ms-sm-auto px-md-4">
                {% include 'includes/breadcrumb.html' %}
                {% include 'includes/messages.html' %}
                
                {% block content %}{% endblock %}
            </main>
        </div>
    </main>
    
    {% include 'includes/footer.html' %}
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JS -->
    <script src="{% static 'js/main.js' %}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## 7. 次のステップ

1. **Djangoプロジェクトのセットアップ**
   - プロジェクト作成
   - 設定ファイルの構成
   
2. **モデルの実装**
   - models.pyの作成
   - マイグレーション実行
   
3. **ビューの実装**
   - views.pyの作成
   - フォームの実装
   
4. **テンプレートの実装**
   - HTMLテンプレートの作成
   - Bootstrap統合
   
5. **静的ファイルの作成**
   - CSS、JavaScript
   - ガントチャート描画ライブラリ統合

---

## 8. 使用予定ライブラリ

### 8.1 必須ライブラリ

```txt
# requirements.txt

# Django
Django==4.2.7
django-environ==0.11.2

# データベース
psycopg2-binary==2.9.9  # PostgreSQL

# 履歴管理
django-simple-history==3.4.0

# フォーム・UI
django-crispy-forms==2.1
crispy-bootstrap5==0.7

# 認証
django-allauth==0.57.0  # Phase 2

# ファイル管理
Pillow==10.1.0

# ユーティリティ
python-dateutil==2.8.2

# 開発用
django-debug-toolbar==4.2.0
django-extensions==3.2.3
```

### 8.2 JavaScriptライブラリ

- **Bootstrap 5**: UI フレームワーク
- **Chart.js**: グラフ描画（品質メトリクス）
- **FullCalendar**: カレンダー表示
- **dhtmlxGantt** または **Frappe Gantt**: ガントチャート
- **DataTables**: テーブル拡張（ソート、検索）

---

## 9. まとめ

この設計書では以下を定義しました：

✅ **Djangoアプリケーション構成**: 6つの主要アプリ
✅ **URL設計**: RESTful設計、60以上のエンドポイント
✅ **ビュー設計**: CBV中心、Mixinパターン
✅ **画面一覧**: 40以上の画面
✅ **フォーム設計**: ModelForm活用
✅ **テンプレート設計**: Bootstrap 5ベース

次は実装フェーズに進みます。
