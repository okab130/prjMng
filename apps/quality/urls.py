from django.urls import path
from . import views

app_name = 'quality'

urlpatterns = [
    # バグ管理
    path('bugs/', views.BugListView.as_view(), name='bug_list'),
    path('bugs/create/', views.BugCreateView.as_view(), name='bug_create'),
    path('bugs/<int:pk>/', views.BugDetailView.as_view(), name='bug_detail'),
    path('bugs/<int:pk>/update/', views.BugUpdateView.as_view(), name='bug_update'),
    path('bugs/<int:pk>/delete/', views.BugDeleteView.as_view(), name='bug_delete'),
    
    # テストケース
    path('testcases/', views.TestCaseListView.as_view(), name='testcase_list'),
    path('testcases/create/', views.TestCaseCreateView.as_view(), name='testcase_create'),
    path('testcases/<int:pk>/', views.TestCaseDetailView.as_view(), name='testcase_detail'),
    path('testcases/<int:pk>/update/', views.TestCaseUpdateView.as_view(), name='testcase_update'),
    
    # テスト実行
    path('testcases/<int:testcase_pk>/execute/', views.TestExecutionCreateView.as_view(), name='test_execute'),
    
    # 品質レポート
    path('report/', views.QualityReportView.as_view(), name='quality_report'),
]
