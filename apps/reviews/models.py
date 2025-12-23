from django.db import models
from simple_history.models import HistoricalRecords
from apps.accounts.models import User
from apps.projects.models import AbstractBaseModel, ActiveManager, Project
from apps.tasks.models import Task


class Review(AbstractBaseModel):
    """レビュー"""
    
    class TypeChoices(models.TextChoices):
        DESIGN = 'DESIGN', '設計レビュー'
        CODE = 'CODE', 'コードレビュー'
        TEST = 'TEST', 'テストレビュー'
        DOCUMENT = 'DOCUMENT', 'ドキュメントレビュー'
    
    class StatusChoices(models.TextChoices):
        PLANNED = 'PLANNED', '計画中'
        IN_PROGRESS = 'IN_PROGRESS', '実施中'
        COMPLETED = 'COMPLETED', '完了'
        CANCELLED = 'CANCELLED', 'キャンセル'
    
    class ConclusionChoices(models.TextChoices):
        APPROVED = 'APPROVED', '承認'
        CONDITIONAL = 'CONDITIONAL', '条件付承認'
        REJECTED = 'REJECTED', '差し戻し'
        PENDING = 'PENDING', '未決定'
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    review_number = models.CharField(
        max_length=20, 
        verbose_name='レビュー番号'
    )
    title = models.CharField(max_length=200, verbose_name='タイトル')
    review_type = models.CharField(
        max_length=20, 
        choices=TypeChoices.choices, 
        default=TypeChoices.CODE,
        verbose_name='レビュータイプ'
    )
    description = models.TextField(blank=True, verbose_name='説明')
    
    # 対象
    target_description = models.TextField(verbose_name='レビュー対象')
    target_document = models.FileField(
        upload_to='review_documents/', 
        blank=True, 
        null=True, 
        verbose_name='対象ドキュメント'
    )
    
    # 日時・場所
    scheduled_at = models.DateTimeField(verbose_name='実施予定日時')
    actual_start_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='開始日時'
    )
    actual_end_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='終了日時'
    )
    location = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='場所'
    )
    
    # ステータス
    status = models.CharField(
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.PLANNED,
        verbose_name='ステータス'
    )
    conclusion = models.CharField(
        max_length=20, 
        choices=ConclusionChoices.choices, 
        default=ConclusionChoices.PENDING,
        verbose_name='結論'
    )
    
    # 議事録
    minutes = models.TextField(blank=True, verbose_name='議事録')
    decisions = models.TextField(blank=True, verbose_name='決定事項')
    topics = models.TextField(blank=True, verbose_name='課題')
    
    # 関連
    related_task = models.ForeignKey(
        Task, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviews',
        verbose_name='関連タスク'
    )
    
    objects = ActiveManager()
    all_objects = models.Manager()
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'reviews'
        verbose_name = 'レビュー'
        verbose_name_plural = 'レビュー'
        ordering = ['-scheduled_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['review_type', 'scheduled_at']),
        ]
        unique_together = [['project', 'review_number']]
    
    def __str__(self):
        return f"{self.review_number} - {self.title}"
    
    @property
    def duration_minutes(self):
        """レビュー所要時間（分）"""
        if self.actual_start_at and self.actual_end_at:
            delta = self.actual_end_at - self.actual_start_at
            return int(delta.total_seconds() / 60)
        return None


class ReviewParticipant(models.Model):
    """レビュー参加者"""
    
    class RoleChoices(models.TextChoices):
        MODERATOR = 'MODERATOR', 'モデレーター'
        REVIEWER = 'REVIEWER', 'レビュアー'
        AUTHOR = 'AUTHOR', '作成者'
        OBSERVER = 'OBSERVER', '参加者'
    
    review = models.ForeignKey(
        Review, 
        on_delete=models.CASCADE, 
        related_name='participants'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20, 
        choices=RoleChoices.choices, 
        default=RoleChoices.REVIEWER,
        verbose_name='役割'
    )
    attended = models.BooleanField(default=False, verbose_name='出席')
    
    class Meta:
        db_table = 'review_participants'
        verbose_name = 'レビュー参加者'
        verbose_name_plural = 'レビュー参加者'
        unique_together = [['review', 'user']]
    
    def __str__(self):
        return f"{self.review.review_number} - {self.user.display_name} ({self.role})"


class ReviewIssue(AbstractBaseModel):
    """指摘事項"""
    
    class SeverityChoices(models.TextChoices):
        CRITICAL = 'CRITICAL', '重大'
        MAJOR = 'MAJOR', '中'
        MINOR = 'MINOR', '軽微'
        SUGGESTION = 'SUGGESTION', '提案'
    
    class StatusChoices(models.TextChoices):
        OPEN = 'OPEN', '未対応'
        IN_PROGRESS = 'IN_PROGRESS', '対応中'
        RESOLVED = 'RESOLVED', '対応済'
        VERIFIED = 'VERIFIED', '確認済'
        REJECTED = 'REJECTED', '却下'
    
    review = models.ForeignKey(
        Review, 
        on_delete=models.CASCADE, 
        related_name='issues'
    )
    issue_number = models.CharField(max_length=20, verbose_name='指摘番号')
    description = models.TextField(verbose_name='指摘内容')
    severity = models.CharField(
        max_length=20, 
        choices=SeverityChoices.choices, 
        default=SeverityChoices.MAJOR,
        verbose_name='重要度'
    )
    status = models.CharField(
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.OPEN,
        verbose_name='ステータス'
    )
    
    # 担当
    reporter = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='reported_review_issues',
        verbose_name='報告者'
    )
    assignee = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_review_issues',
        verbose_name='担当者'
    )
    
    # 該当箇所
    location = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='該当箇所'
    )
    page_number = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name='ページ番号'
    )
    line_number = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name='行番号'
    )
    file_name = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='ファイル名'
    )
    
    # 対応
    response = models.TextField(blank=True, verbose_name='対応内容')
    resolved_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='対応完了日時'
    )
    verifier = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_review_issues',
        verbose_name='確認者'
    )
    verified_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='確認日時'
    )
    
    objects = ActiveManager()
    all_objects = models.Manager()
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'review_issues'
        verbose_name = '指摘事項'
        verbose_name_plural = '指摘事項'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['review', 'status']),
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['severity', 'status']),
        ]
    
    def __str__(self):
        return f"{self.issue_number} - {self.description[:50]}"
