from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import User


class ProfileView(LoginRequiredMixin, DetailView):
    """プロフィール表示"""
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """プロフィール編集"""
    model = User
    template_name = 'accounts/profile_edit.html'
    fields = ['display_name', 'email', 'department', 'phone', 'avatar']
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
