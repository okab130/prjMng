from django import forms
from django.core.exceptions import ValidationError
from .models import Task, TaskComment, SystemCategory, MajorCategory, MinorCategory
from apps.projects.models import Project
from apps.accounts.models import User


class TaskForm(forms.ModelForm):
    """タスク作成・編集フォーム"""
    
    class Meta:
        model = Task
        fields = [
            'project', 'system_category', 'major_category', 'minor_category',
            'parent', 'title', 'description',
            'assignee', 'status', 'priority', 'planned_start_date',
            'planned_end_date', 'actual_start_date', 'actual_end_date',
            'estimated_hours', 'actual_hours', 'progress_rate'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select', 'id': 'id_project'}),
            'system_category': forms.Select(attrs={'class': 'form-select', 'id': 'id_system_category'}),
            'major_category': forms.Select(attrs={'class': 'form-select', 'id': 'id_major_category'}),
            'minor_category': forms.Select(attrs={'class': 'form-select', 'id': 'id_minor_category'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
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
        
        # 初期状態では空のクエリセット
        self.fields['system_category'].queryset = SystemCategory.objects.none()
        self.fields['major_category'].queryset = MajorCategory.objects.none()
        self.fields['minor_category'].queryset = MinorCategory.objects.none()
        
        # プロジェクトが選択されている場合
        if 'project' in self.data:
            try:
                project_id = int(self.data.get('project'))
                self.fields['system_category'].queryset = SystemCategory.objects.filter(
                    project_id=project_id, is_deleted=False
                ).order_by('order', 'name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # 編集時
            self.fields['system_category'].queryset = SystemCategory.objects.filter(
                project=self.instance.project, is_deleted=False
            ).order_by('order', 'name')
            if self.instance.system_category:
                self.fields['major_category'].queryset = MajorCategory.objects.filter(
                    system_category=self.instance.system_category, is_deleted=False
                ).order_by('order', 'name')
            if self.instance.major_category:
                self.fields['minor_category'].queryset = MinorCategory.objects.filter(
                    major_category=self.instance.major_category, is_deleted=False
                ).order_by('order', 'name')
        
        # システム名が選択されている場合
        if 'system_category' in self.data:
            try:
                system_id = int(self.data.get('system_category'))
                self.fields['major_category'].queryset = MajorCategory.objects.filter(
                    system_category_id=system_id, is_deleted=False
                ).order_by('order', 'name')
            except (ValueError, TypeError):
                pass
        
        # 大分類が選択されている場合
        if 'major_category' in self.data:
            try:
                major_id = int(self.data.get('major_category'))
                self.fields['minor_category'].queryset = MinorCategory.objects.filter(
                    major_category_id=major_id, is_deleted=False
                ).order_by('order', 'name')
            except (ValueError, TypeError):
                pass
        
        # 分類フィールドの設定
        self.fields['system_category'].empty_label = '選択してください'
        self.fields['major_category'].empty_label = '選択してください'
        self.fields['minor_category'].empty_label = '選択してください'
        
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
