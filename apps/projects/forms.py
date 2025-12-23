from django import forms
from django.core.exceptions import ValidationError
from .models import Project, Milestone
from apps.accounts.models import User


class ProjectForm(forms.ModelForm):
    """プロジェクト作成・編集フォーム"""
    
    class Meta:
        model = Project
        fields = [
            'project_code', 'name', 'description', 'status',
            'start_date', 'end_date'
        ]
        widgets = {
            'project_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: PRJ-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError('開始日は終了日より前である必要があります。')
        
        return cleaned_data


class MilestoneForm(forms.ModelForm):
    """マイルストーン作成・編集フォーム"""
    
    class Meta:
        model = Milestone
        fields = ['name', 'description', 'target_date', 'actual_date', 'status', 'criteria', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actual_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['actual_date'].required = False
        self.fields['criteria'].required = False
        self.fields['order'].initial = 1
    
    def clean(self):
        cleaned_data = super().clean()
        target_date = cleaned_data.get('target_date')
        actual_date = cleaned_data.get('actual_date')
        
        if target_date and actual_date and actual_date < target_date:
            # 警告だけで、エラーにはしない（早期達成もあり得る）
            pass
        
        return cleaned_data
