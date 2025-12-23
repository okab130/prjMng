from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # プロジェクト一覧・詳細
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    
    # メンバー管理
    path('<int:project_pk>/members/', views.ProjectMemberListView.as_view(), name='member_list'),
    path('<int:project_pk>/members/add/', views.ProjectMemberAddView.as_view(), name='member_add'),
    path('<int:project_pk>/members/<int:pk>/remove/', views.ProjectMemberRemoveView.as_view(), name='member_remove'),
    
    # マイルストーン
    path('<int:project_pk>/milestones/', views.MilestoneListView.as_view(), name='milestone_list'),
    path('<int:project_pk>/milestones/create/', views.MilestoneCreateView.as_view(), name='milestone_create'),
    path('<int:project_pk>/milestones/<int:pk>/update/', views.MilestoneUpdateView.as_view(), name='milestone_update'),
    path('<int:project_pk>/milestones/<int:pk>/delete/', views.MilestoneDeleteView.as_view(), name='milestone_delete'),
]
