from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Review, ReviewIssue


class ReviewListView(LoginRequiredMixin, ListView):
    """レビュー一覧"""
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 20
    
    def get_queryset(self):
        return Review.objects.select_related('project').order_by('-scheduled_at')


class ReviewDetailView(LoginRequiredMixin, DetailView):
    """レビュー詳細"""
    model = Review
    template_name = 'reviews/review_detail.html'
    context_object_name = 'review'
    
    def get_queryset(self):
        return Review.objects.select_related('project').prefetch_related(
            'participants__user', 'issues__reporter', 'issues__assignee'
        )


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """レビュー作成"""
    model = Review
    template_name = 'reviews/review_form.html'
    fields = ['project', 'review_number', 'title', 'review_type', 
              'description', 'target_description', 'scheduled_at', 'location']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('reviews:review_detail', kwargs={'pk': self.object.pk})


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    """レビュー更新"""
    model = Review
    template_name = 'reviews/review_form.html'
    fields = ['status', 'conclusion', 'actual_start_at', 'actual_end_at',
              'minutes', 'decisions', 'topics']
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('reviews:review_detail', kwargs={'pk': self.object.pk})


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    """レビュー削除"""
    model = Review
    template_name = 'reviews/review_confirm_delete.html'
    success_url = reverse_lazy('reviews:review_list')


class ReviewIssueCreateView(LoginRequiredMixin, CreateView):
    """指摘事項作成"""
    model = ReviewIssue
    template_name = 'reviews/issue_form.html'
    fields = ['issue_number', 'description', 'severity', 'assignee',
              'location', 'page_number', 'line_number', 'file_name']
    
    def form_valid(self, form):
        form.instance.review_id = self.kwargs['review_pk']
        form.instance.reporter = self.request.user
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('reviews:review_detail', 
                          kwargs={'pk': self.kwargs['review_pk']})


class ReviewIssueUpdateView(LoginRequiredMixin, UpdateView):
    """指摘事項更新"""
    model = ReviewIssue
    template_name = 'reviews/issue_form.html'
    fields = ['status', 'response', 'resolved_at', 'verified_at']
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        if form.instance.status == 'VERIFIED':
            form.instance.verifier = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('reviews:review_detail', 
                          kwargs={'pk': self.kwargs['review_pk']})
