from django import forms
from django.core.exceptions import ValidationError
from .models import Task, TaskComment
from apps.projects.models import Project
from apps.accounts.models import User


class TaskForm(forms.ModelForm):
    """タスク作成・編集フォーム"""
    
    class Meta:
        model = Task
        fields = [
            'project', 'parent', 'task_number', 'title', 'description',
            'assignee', 'status', 'priority', 'planned_start_date',
            'planned_end_date', 'actual_start_date', 'actual_end_date',
            'estimated_hours', 'actual_hours', 'progress_rate'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'task_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: TSK-001'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'assignee': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'planned_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'planned_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'actual_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'actual_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estimated_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.5'}),
            'actual_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.5'}),
            'progress_rate': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # プロジェクトは削除されていないもののみ
        self.fields['project'].queryset = Project.objects.filter(is_deleted=False)
        self.fields['project'].empty_label = '選択してください'
        
        # 担当者はアクティブなユーザーのみ
        self.fields['assignee'].queryset = User.objects.filter(is_active=True)
        self.fields['assignee'].empty_label = '未割当'
        self.fields['assignee'].required = False
        
        # 親タスクは削除されていないもののみ
        self.fields['parent'].queryset = Task.objects.filter(is_deleted=False)
        self.fields['parent'].empty_label = 'なし'
        self.fields['parent'].required = False
        
        # 任意項目の設定
        self.fields['description'].required = False
        self.fields['actual_start_date'].required = False
        self.fields['actual_end_date'].required = False
        self.fields['estimated_hours'].required = False
        self.fields['actual_hours'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        planned_start = cleaned_data.get('planned_start_date')
        planned_end = cleaned_data.get('planned_end_date')
        actual_start = cleaned_data.get('actual_start_date')
        actual_end = cleaned_data.get('actual_end_date')
        
        # 予定日の整合性チェック
        if planned_start and planned_end and planned_start > planned_end:
            raise ValidationError('開始予定日は終了予定日より前である必要があります。')
        
        # 実績日の整合性チェック
        if actual_start and actual_end and actual_start > actual_end:
            raise ValidationError('実績開始日は実績終了日より前である必要があります。')
        
        return cleaned_data


class TaskCommentForm(forms.ModelForm):
    """タスクコメントフォーム"""
    
    class Meta:
        model = TaskComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'コメントを入力してください...'
            })
        }
