from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # レビュー一覧・詳細
    path('', views.ReviewListView.as_view(), name='review_list'),
    path('create/', views.ReviewCreateView.as_view(), name='review_create'),
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),
    path('<int:pk>/update/', views.ReviewUpdateView.as_view(), name='review_update'),
    path('<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    
    # 指摘事項
    path('<int:review_pk>/issues/create/', views.ReviewIssueCreateView.as_view(), name='issue_create'),
    path('<int:review_pk>/issues/<int:pk>/update/', views.ReviewIssueUpdateView.as_view(), name='issue_update'),
]
