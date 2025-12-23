from django.db import models
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
from apps.accounts.models import User
from apps.projects.models import AbstractBaseModel, ActiveManager, Project


class Task(AbstractBaseModel):
    """タスク"""
    
    class StatusChoices(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', '未着手'
        IN_PROGRESS = 'IN_PROGRESS', '進行中'
        COMPLETED = 'COMPLETED', '完了'
        ON_HOLD = 'ON_HOLD', '保留'
    
    class PriorityChoices(models.TextChoices):
        HIGH = 'HIGH', '高'
        MEDIUM = 'MEDIUM', '中'
        LOW = 'LOW', '低'
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='tasks'
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subtasks',
        verbose_name='親タスク'
    )
    task_number = models.CharField(max_length=20, verbose_name='タスク番号')
    title = models.CharField(max_length=200, verbose_name='タイトル')
    description = models.TextField(blank=True, verbose_name='説明')
    assignee = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tasks',
        verbose_name='担当者'
    )
    status = models.CharField(
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.NOT_STARTED,
        verbose_name='ステータス'
    )
    priority = models.CharField(
        max_length=10, 
        choices=PriorityChoices.choices, 
        default=PriorityChoices.MEDIUM,
        verbose_name='優先度'
    )
    
    # 日程
    planned_start_date = models.DateField(verbose_name='開始予定日')
    planned_end_date = models.DateField(verbose_name='終了予定日')
    actual_start_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='開始実績日'
    )
    actual_end_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='終了実績日'
    )
    
    # 工数
    estimated_hours = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0, 
        verbose_name='見積工数(h)'
    )
    actual_hours = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0, 
        verbose_name='実績工数(h)'
    )
    progress_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0, 
        verbose_name='進捗率(%)'
    )
    
    # WBS
    wbs_code = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name='WBSコード'
    )
    level = models.IntegerField(default=0, verbose_name='階層レベル')
    
    objects = ActiveManager()
    all_objects = models.Manager()
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'タスク'
        verbose_name_plural = 'タスク'
        ordering = ['wbs_code', 'planned_start_date']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['planned_start_date', 'planned_end_date']),
        ]
        unique_together = [['project', 'task_number']]
    
    def __str__(self):
        return f"{self.task_number} - {self.title}"
    
    def clean(self):
        if self.planned_start_date and self.planned_end_date:
            if self.planned_start_date > self.planned_end_date:
                raise ValidationError('終了予定日は開始予定日より後である必要があります')
        
        # 親タスクの循環参照チェック
        if self.parent:
            current = self.parent
            visited = set()
            while current:
                if current.id == self.id or current.id in visited:
                    raise ValidationError('タスクの循環参照が検出されました')
                visited.add(current.id)
                current = current.parent


class TaskDependency(models.Model):
    """タスク依存関係"""
    
    class DependencyTypeChoices(models.TextChoices):
        FINISH_TO_START = 'FS', '終了-開始 (FS)'
        START_TO_START = 'SS', '開始-開始 (SS)'
        FINISH_TO_FINISH = 'FF', '終了-終了 (FF)'
        START_TO_FINISH = 'SF', '開始-終了 (SF)'
    
    predecessor = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='successors', 
        verbose_name='前提タスク'
    )
    successor = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='predecessors', 
        verbose_name='後続タスク'
    )
    dependency_type = models.CharField(
        max_length=2, 
        choices=DependencyTypeChoices.choices, 
        default=DependencyTypeChoices.FINISH_TO_START,
        verbose_name='依存タイプ'
    )
    lag_days = models.IntegerField(default=0, verbose_name='遅延日数')
    
    class Meta:
        db_table = 'task_dependencies'
        verbose_name = 'タスク依存関係'
        verbose_name_plural = 'タスク依存関係'
        unique_together = [['predecessor', 'successor']]
    
    def __str__(self):
        return f"{self.predecessor.task_number} -> {self.successor.task_number} ({self.dependency_type})"
    
    def clean(self):
        if self.predecessor.project != self.successor.project:
            raise ValidationError('異なるプロジェクトのタスク間に依存関係は設定できません')
        
        if self.predecessor == self.successor:
            raise ValidationError('同じタスクに依存関係は設定できません')


class TaskComment(AbstractBaseModel):
    """タスクコメント"""
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(verbose_name='コメント')
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        db_table = 'task_comments'
        verbose_name = 'タスクコメント'
        verbose_name_plural = 'タスクコメント'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task.task_number} - {self.user.display_name}"
