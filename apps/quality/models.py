from django.db import models
from simple_history.models import HistoricalRecords
from apps.accounts.models import User
from apps.projects.models import AbstractBaseModel, ActiveManager, Project
from apps.tasks.models import Task


class Bug(AbstractBaseModel):
    """バグ"""
    
    class StatusChoices(models.TextChoices):
        NEW = 'NEW', '新規'
        IN_PROGRESS = 'IN_PROGRESS', '対応中'
        FIXED = 'FIXED', '修正済'
        VERIFIED = 'VERIFIED', '確認済'
        REJECTED = 'REJECTED', '却下'
        ON_HOLD = 'ON_HOLD', '保留'
        REOPENED = 'REOPENED', '再オープン'
    
    class PriorityChoices(models.TextChoices):
        CRITICAL = 'CRITICAL', '致命的'
        HIGH = 'HIGH', '重大'
        MEDIUM = 'MEDIUM', '中'
        LOW = 'LOW', '軽微'
    
    class SeverityChoices(models.TextChoices):
        HIGH = 'HIGH', '高'
        MEDIUM = 'MEDIUM', '中'
        LOW = 'LOW', '低'
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='bugs'
    )
    bug_number = models.CharField(max_length=20, verbose_name='バグ番号')
    title = models.CharField(max_length=200, verbose_name='タイトル')
    description = models.TextField(verbose_name='詳細説明')
    
    # 担当・報告
    reporter = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='reported_bugs',
        verbose_name='報告者'
    )
    assignee = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_bugs',
        verbose_name='担当者'
    )
    
    # ステータス・優先度
    status = models.CharField(
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.NEW,
        verbose_name='ステータス'
    )
    priority = models.CharField(
        max_length=10, 
        choices=PriorityChoices.choices, 
        default=PriorityChoices.MEDIUM,
        verbose_name='優先度'
    )
    severity = models.CharField(
        max_length=10, 
        choices=SeverityChoices.choices, 
        default=SeverityChoices.MEDIUM,
        verbose_name='重要度'
    )
    
    # 分類
    category = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name='カテゴリ'
    )
    module = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='モジュール'
    )
    
    # バージョン
    found_version = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name='発見バージョン'
    )
    fixed_version = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name='修正バージョン'
    )
    
    # 詳細情報
    reproduction_steps = models.TextField(
        blank=True, 
        verbose_name='再現手順'
    )
    environment = models.TextField(
        blank=True, 
        verbose_name='環境情報'
    )
    fix_description = models.TextField(
        blank=True, 
        verbose_name='修正内容'
    )
    test_result = models.TextField(
        blank=True, 
        verbose_name='テスト結果'
    )
    
    # 日程
    found_date = models.DateField(auto_now_add=True, verbose_name='発見日')
    fixed_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='修正日'
    )
    verified_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='確認日'
    )
    
    # 関連
    related_task = models.ForeignKey(
        Task, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='related_bugs',
        verbose_name='関連タスク'
    )
    
    objects = ActiveManager()
    all_objects = models.Manager()
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'bugs'
        verbose_name = 'バグ'
        verbose_name_plural = 'バグ'
        ordering = ['-found_date', '-priority']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['priority', 'status']),
        ]
        unique_together = [['project', 'bug_number']]
    
    def __str__(self):
        return f"{self.bug_number} - {self.title}"


class BugComment(AbstractBaseModel):
    """バグコメント"""
    bug = models.ForeignKey(
        Bug, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(verbose_name='コメント')
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        db_table = 'bug_comments'
        verbose_name = 'バグコメント'
        verbose_name_plural = 'バグコメント'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.bug.bug_number} - {self.user.display_name}"


class TestCase(AbstractBaseModel):
    """テストケース"""
    
    class CategoryChoices(models.TextChoices):
        UNIT = 'UNIT', '単体テスト'
        INTEGRATION = 'INTEGRATION', '結合テスト'
        SYSTEM = 'SYSTEM', 'システムテスト'
        ACCEPTANCE = 'ACCEPTANCE', '受入テスト'
    
    class PriorityChoices(models.TextChoices):
        HIGH = 'HIGH', '高'
        MEDIUM = 'MEDIUM', '中'
        LOW = 'LOW', '低'
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='test_cases'
    )
    test_case_number = models.CharField(
        max_length=20, 
        verbose_name='テストケース番号'
    )
    title = models.CharField(max_length=200, verbose_name='タイトル')
    category = models.CharField(
        max_length=20, 
        choices=CategoryChoices.choices, 
        default=CategoryChoices.UNIT,
        verbose_name='カテゴリ'
    )
    priority = models.CharField(
        max_length=10, 
        choices=PriorityChoices.choices, 
        default=PriorityChoices.MEDIUM,
        verbose_name='優先度'
    )
    
    # テスト内容
    precondition = models.TextField(blank=True, verbose_name='前提条件')
    test_steps = models.TextField(verbose_name='テスト手順')
    expected_result = models.TextField(verbose_name='期待結果')
    
    # 分類
    target_function = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='対象機能'
    )
    module = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='モジュール'
    )
    
    # 関連
    related_task = models.ForeignKey(
        Task, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='test_cases',
        verbose_name='関連タスク'
    )
    
    objects = ActiveManager()
    all_objects = models.Manager()
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'test_cases'
        verbose_name = 'テストケース'
        verbose_name_plural = 'テストケース'
        ordering = ['test_case_number']
        indexes = [
            models.Index(fields=['project', 'category']),
        ]
        unique_together = [['project', 'test_case_number']]
    
    def __str__(self):
        return f"{self.test_case_number} - {self.title}"


class TestExecution(AbstractBaseModel):
    """テスト実行"""
    
    class ResultChoices(models.TextChoices):
        PASSED = 'PASSED', '成功'
        FAILED = 'FAILED', '失敗'
        NOT_EXECUTED = 'NOT_EXECUTED', '未実施'
        NOT_APPLICABLE = 'NOT_APPLICABLE', 'N/A'
    
    test_case = models.ForeignKey(
        TestCase, 
        on_delete=models.CASCADE, 
        related_name='executions'
    )
    executor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='実行者'
    )
    executed_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='実行日時'
    )
    result = models.CharField(
        max_length=20, 
        choices=ResultChoices.choices, 
        default=ResultChoices.NOT_EXECUTED,
        verbose_name='結果'
    )
    actual_result = models.TextField(
        blank=True, 
        verbose_name='実績結果'
    )
    execution_time = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='実行時間(分)'
    )
    notes = models.TextField(blank=True, verbose_name='備考')
    
    # 関連バグ
    related_bug = models.ForeignKey(
        Bug, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='test_executions',
        verbose_name='関連バグ'
    )
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        db_table = 'test_executions'
        verbose_name = 'テスト実行'
        verbose_name_plural = 'テスト実行'
        ordering = ['-executed_at']
        indexes = [
            models.Index(fields=['test_case', 'executed_at']),
            models.Index(fields=['executor', 'result']),
        ]
    
    def __str__(self):
        return f"{self.test_case.test_case_number} - {self.result} ({self.executed_at})"


class QualityMetric(AbstractBaseModel):
    """品質メトリクス"""
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='quality_metrics'
    )
    metric_name = models.CharField(max_length=100, verbose_name='指標名')
    metric_type = models.CharField(max_length=50, verbose_name='指標タイプ')
    target_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='目標値'
    )
    actual_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='実績値'
    )
    unit = models.CharField(max_length=20, blank=True, verbose_name='単位')
    measured_at = models.DateField(verbose_name='測定日')
    notes = models.TextField(blank=True, verbose_name='備考')
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        db_table = 'quality_metrics'
        verbose_name = '品質メトリクス'
        verbose_name_plural = '品質メトリクス'
        ordering = ['-measured_at']
        indexes = [
            models.Index(fields=['project', 'measured_at']),
            models.Index(fields=['metric_type', 'measured_at']),
        ]
    
    def __str__(self):
        return f"{self.project.project_code} - {self.metric_name} ({self.measured_at})"
    
    @property
    def achievement_rate(self):
        """達成率を計算"""
        if self.target_value == 0:
            return 0
        return (self.actual_value / self.target_value) * 100
