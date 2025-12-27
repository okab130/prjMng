from django.db import models
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
from apps.accounts.models import User
from apps.projects.models import AbstractBaseModel, ActiveManager, Project


class SystemCategory(AbstractBaseModel):
    """システム名マスタ"""
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='system_categories',
        verbose_name='プロジェクト'
    )
    code = models.CharField(max_length=20, verbose_name='システムコード')
    name = models.CharField(max_length=100, verbose_name='システム名')
    description = models.TextField(blank=True, verbose_name='説明')
    order = models.IntegerField(default=0, verbose_name='表示順')
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        db_table = 'system_categories'
        verbose_name = 'システム分類'
        verbose_name_plural = 'システム分類'
        ordering = ['project', 'order', 'code']
        unique_together = [['project', 'code']]
        indexes = [
            models.Index(fields=['project', 'order']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class MajorCategory(AbstractBaseModel):
    """大分類マスタ"""
    
    system_category = models.ForeignKey(
        SystemCategory,
        on_delete=models.CASCADE,
        related_name='major_categories',
        verbose_name='システム名'
    )
    code = models.CharField(max_length=20, verbose_name='大分類コード')
    name = models.CharField(max_length=100, verbose_name='大分類名')
    description = models.TextField(blank=True, verbose_name='説明')
    order = models.IntegerField(default=0, verbose_name='表示順')
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        db_table = 'major_categories'
        verbose_name = '大分類'
        verbose_name_plural = '大分類'
        ordering = ['system_category', 'order', 'code']
        unique_together = [['system_category', 'code']]
        indexes = [
            models.Index(fields=['system_category', 'order']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def full_path(self):
        """階層パス取得"""
        return f"{self.system_category.name} > {self.name}"


class MinorCategory(AbstractBaseModel):
    """中分類マスタ"""
    
    major_category = models.ForeignKey(
        MajorCategory,
        on_delete=models.CASCADE,
        related_name='minor_categories',
        verbose_name='大分類'
    )
    code = models.CharField(max_length=20, verbose_name='中分類コード')
    name = models.CharField(max_length=100, verbose_name='中分類名')
    description = models.TextField(blank=True, verbose_name='説明')
    order = models.IntegerField(default=0, verbose_name='表示順')
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        db_table = 'minor_categories'
        verbose_name = '中分類'
        verbose_name_plural = '中分類'
        ordering = ['major_category', 'order', 'code']
        unique_together = [['major_category', 'code']]
        indexes = [
            models.Index(fields=['major_category', 'order']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def full_path(self):
        """階層パス取得"""
        return f"{self.major_category.system_category.name} > {self.major_category.name} > {self.name}"
    
    @property
    def system_category(self):
        """システム分類取得"""
        return self.major_category.system_category


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
    system_category = models.ForeignKey(
        SystemCategory,
        on_delete=models.PROTECT,
        related_name='tasks',
        verbose_name='システム名',
        null=True,
        blank=True
    )
    major_category = models.ForeignKey(
        MajorCategory,
        on_delete=models.PROTECT,
        related_name='tasks',
        verbose_name='大分類',
        null=True,
        blank=True
    )
    minor_category = models.ForeignKey(
        MinorCategory,
        on_delete=models.PROTECT,
        related_name='tasks',
        verbose_name='中分類',
        null=True,
        blank=True
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
            models.Index(fields=['system_category']),
            models.Index(fields=['major_category']),
            models.Index(fields=['minor_category']),
        ]
        unique_together = [['project', 'task_number']]
    
    def __str__(self):
        return f"{self.task_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        """タスク番号の自動採番 + ステータス自動更新"""
        
        # タスク番号の自動採番
        if not self.pk and not self.task_number:
            from django.db import transaction
            
            with transaction.atomic():
                # プロジェクト内の最大タスク番号を取得（ロック付き）
                last_task = Task.objects.select_for_update().filter(
                    project=self.project,
                    is_deleted=False
                ).order_by('-task_number').first()
                
                if last_task and last_task.task_number:
                    try:
                        # 数字部分を抽出して+1
                        last_number = int(last_task.task_number)
                        self.task_number = f"{last_number + 1:03d}"
                    except ValueError:
                        # 既存データが数字でない場合は001から開始
                        self.task_number = "001"
                else:
                    # 最初のタスク
                    self.task_number = "001"
        
        # ステータス自動更新
        old_status = None
        if self.pk:
            try:
                old_task = Task.objects.get(pk=self.pk)
                old_status = old_task.status
            except Task.DoesNotExist:
                pass
        
        # 実績終了日が入力されている場合 → 完了
        if self.actual_end_date:
            self.status = Task.StatusChoices.COMPLETED
            self.progress_rate = 100
        # 実績終了日が削除された場合の処理
        elif not self.actual_end_date and old_status == Task.StatusChoices.COMPLETED:
            # 実績開始日がある場合は進行中に
            if self.actual_start_date:
                self.status = Task.StatusChoices.IN_PROGRESS
            else:
                self.status = Task.StatusChoices.NOT_STARTED
        # 実績開始日が入力され、実績終了日が未入力の場合 → 進行中
        elif self.actual_start_date and not self.actual_end_date:
            if self.status == Task.StatusChoices.NOT_STARTED:
                self.status = Task.StatusChoices.IN_PROGRESS
        
        super().save(*args, **kwargs)
    
    def clean(self):
        if self.planned_start_date and self.planned_end_date:
            if self.planned_start_date > self.planned_end_date:
                raise ValidationError('終了予定日は開始予定日より後である必要があります')
        
        # 実績日のバリデーション
        if self.actual_start_date and self.actual_end_date:
            if self.actual_start_date > self.actual_end_date:
                raise ValidationError('実績終了日は実績開始日より後である必要があります')
        
        # 階層整合性チェック
        if self.minor_category and self.major_category:
            if self.minor_category.major_category != self.major_category:
                raise ValidationError('中分類と大分類の関係が正しくありません')
        
        if self.major_category and self.system_category:
            if self.major_category.system_category != self.system_category:
                raise ValidationError('大分類とシステム名の関係が正しくありません')
        
        if self.system_category and self.project:
            if self.system_category.project != self.project:
                raise ValidationError('システム名とプロジェクトの関係が正しくありません')
        
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
