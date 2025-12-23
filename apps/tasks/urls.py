from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # タスク一覧・詳細
    path('', views.TaskListView.as_view(), name='task_list'),
    path('create/', views.TaskCreateView.as_view(), name='task_create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    
    # カレンダー・ガントチャート
    path('calendar/', views.TaskCalendarView.as_view(), name='task_calendar'),
    path('gantt/', views.TaskGanttView.as_view(), name='task_gantt'),
    
    # コメント
    path('<int:task_pk>/comments/add/', views.TaskCommentAddView.as_view(), name='comment_add'),
]
