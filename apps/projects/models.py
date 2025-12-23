from django.db import models
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
from apps.accounts.models import User


class AbstractBaseModel(models.Model):
    """共通フィールドを持つ抽象ベースモデル"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='+',
        verbose_name='作成者'
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='+',
        verbose_name='更新者'
    )
    is_deleted = models.BooleanField(default=False, verbose_name='削除フラグ')
    
    class Meta:
        abstract = True


class ActiveManager(models.Manager):
    """削除されていないレコードのみを返すマネージャー"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Project(AbstractBaseModel):
    """プロジェクト"""
    
    class StatusChoices(models.TextChoices):
        PLANNING = 'PLANNING', '計画中'
        IN_PROGRESS = 'IN_PROGRESS', '進行中'
        COMPLETED = 'COMPLETED', '完了'
        SUSPENDED = 'SUSPENDED', '中止'
    
    project_code = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='プロジェクトコード'
    )
    name = models.CharField(max_length=200, verbose_name='プロジェクト名')
    description = models.TextField(blank=True, verbose_name='説明')
    status = models.CharField(
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.PLANNING,
        verbose_name='ステータス'
    )
    start_date = models.DateField(verbose_name='開始日')
    end_date = models.DateField(verbose_name='終了日')
    actual_start_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='実績開始日'
    )
    actual_end_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='実績終了日'
    )
    budget = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='予算'
    )
    progress_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0, 
        verbose_name='進捗率(%)'
    )
    
    objects = ActiveManager()
    all_objects = models.Manager()
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'projects'
        verbose_name = 'プロジェクト'
        verbose_name_plural = 'プロジェクト'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['project_code']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.name}"
    
    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('終了日は開始日より後である必要があります')


class ProjectMember(AbstractBaseModel):
    """プロジェクトメンバー"""
    
    class RoleChoices(models.TextChoices):
        PM = 'PM', 'プロジェクトマネージャー'
        LEADER = 'LEADER', 'リーダー'
        MEMBER = 'MEMBER', 'メンバー'
        VIEWER = 'VIEWER', '閲覧者'
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='members'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='project_memberships'
    )
    role = models.CharField(
        max_length=10, 
        choices=RoleChoices.choices, 
        default=RoleChoices.MEMBER,
        verbose_name='役割'
    )
    joined_at = models.DateField(auto_now_add=True, verbose_name='参加日')
    left_at = models.DateField(null=True, blank=True, verbose_name='離脱日')
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        db_table = 'project_members'
        verbose_name = 'プロジェクトメンバー'
        verbose_name_plural = 'プロジェクトメンバー'
        unique_together = [['project', 'user']]
        indexes = [
            models.Index(fields=['project', 'role']),
        ]
    
    def __str__(self):
        return f"{self.project.name} - {self.user.display_name} ({self.role})"


class Milestone(AbstractBaseModel):
    """マイルストーン"""
    
    class StatusChoices(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', '未達成'
        ACHIEVED = 'ACHIEVED', '達成'
        DELAYED = 'DELAYED', '遅延'
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='milestones'
    )
    name = models.CharField(max_length=200, verbose_name='マイルストーン名')
    description = models.TextField(blank=True, verbose_name='説明')
    target_date = models.DateField(verbose_name='目標日')
    actual_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='達成日'
    )
    status = models.CharField(
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.NOT_STARTED,
        verbose_name='ステータス'
    )
    criteria = models.TextField(blank=True, verbose_name='達成基準')
    order = models.IntegerField(default=0, verbose_name='表示順')
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        db_table = 'milestones'
        verbose_name = 'マイルストーン'
        verbose_name_plural = 'マイルストーン'
        ordering = ['order', 'target_date']
        indexes = [
            models.Index(fields=['project', 'target_date']),
        ]
    
    def __str__(self):
        return f"{self.project.project_code} - {self.name}"
