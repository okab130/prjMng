# Djangoモデル設計書

## 1. データモデル設計方針

### 1.1 設計原則
- **正規化**: 第3正規形を基本とし、パフォーマンス要件に応じて非正規化を検討
- **論理削除**: 重要なデータは物理削除せず、is_deletedフラグで管理
- **監査証跡**: 作成日時、更新日時、作成者、更新者を全テーブルに記録
- **命名規則**: snake_caseを使用、複数形は避ける（Djangoの慣例）
- **制約**: データベースレベルとアプリケーションレベルの両方で整合性を保証

### 1.2 共通フィールド（AbstractBaseModelとして実装）
```python
class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        abstract = True
```

---

## 2. ER図（テキスト表現）

```
[User] 1---* [ProjectMember] *---1 [Project]
  |                                    |
  |                                    |
  +--- 1---* [Task]                   |
  |            |                       |
  |            +--- * [TaskDependency] * ---+
  |            |                            |
  |            +--- * [TaskComment]         |
  |                                         |
  +--- 1---* [Bug] *-----------------------+
  |            |                            |
  |            +--- * [BugComment]          |
  |                                         |
  +--- 1---* [TestCase] *------------------+
  |            |
  |            +--- 1---* [TestExecution]
  |
  +--- 1---* [Review] *--------------------+
  |            |
  |            +--- * [ReviewParticipant]
  |            |
  |            +--- 1---* [ReviewIssue]
  |
  +--- * [Milestone] *---------------------+
  |
  +--- * [QualityMetric] *-----------------+
  |
  +--- * [Notification]
```

---

## 3. モデル詳細設計

### 3.1 ユーザー管理

#### User（ユーザー）
Django標準のAbstractUserを拡張

```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        ADMIN = 'ADMIN', '管理者'
        PM = 'PM', 'プロジェクトマネージャー'
        LEADER = 'LEADER', 'リーダー'
        MEMBER = 'MEMBER', 'メンバー'
        VIEWER = 'VIEWER', '閲覧者'
    
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='社員番号')
    display_name = models.CharField(max_length=100, verbose_name='表示名')
    department = models.CharField(max_length=100, blank=True, verbose_name='所属部署')
    role = models.CharField(max_length=10, choices=RoleChoices.choices, default=RoleChoices.MEMBER)
    phone = models.CharField(max_length=20, blank=True, verbose_name='電話番号')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='アバター')
    is_active = models.BooleanField(default=True, verbose_name='有効')
    last_login_at = models.DateTimeField(null=True, blank=True, verbose_name='最終ログイン')
    
    class Meta:
        db_table = 'users'
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'
        ordering = ['employee_id']
    
    def __str__(self):
        return f"{self.display_name} ({self.employee_id})"
```

---

### 3.2 プロジェクト管理

#### Project（プロジェクト）

```python
class Project(AbstractBaseModel):
    class StatusChoices(models.TextChoices):
        PLANNING = 'PLANNING', '計画中'
        IN_PROGRESS = 'IN_PROGRESS', '進行中'
        COMPLETED = 'COMPLETED', '完了'
        SUSPENDED = 'SUSPENDED', '中止'
    
    project_code = models.CharField(max_length=20, unique=True, verbose_name='プロジェクトコード')
    name = models.CharField(max_length=200, verbose_name='プロジェクト名')
    description = models.TextField(blank=True, verbose_name='説明')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PLANNING)
    start_date = models.DateField(verbose_name='開始日')
    end_date = models.DateField(verbose_name='終了日')
    actual_start_date = models.DateField(null=True, blank=True, verbose_name='実績開始日')
    actual_end_date = models.DateField(null=True, blank=True, verbose_name='実績終了日')
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='予算')
    progress_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='進捗率(%)')
    
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
```

#### ProjectMember（プロジェクトメンバー）

```python
class ProjectMember(AbstractBaseModel):
    class RoleChoices(models.TextChoices):
        PM = 'PM', 'プロジェクトマネージャー'
        LEADER = 'LEADER', 'リーダー'
        MEMBER = 'MEMBER', 'メンバー'
        VIEWER = 'VIEWER', '閲覧者'
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=10, choices=RoleChoices.choices, default=RoleChoices.MEMBER)
    joined_at = models.DateField(auto_now_add=True, verbose_name='参加日')
    left_at = models.DateField(null=True, blank=True, verbose_name='離脱日')
    
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
```

---

### 3.3 スケジュール管理

#### Task（タスク）

```python
class Task(AbstractBaseModel):
    class StatusChoices(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', '未着手'
        IN_PROGRESS = 'IN_PROGRESS', '進行中'
        COMPLETED = 'COMPLETED', '完了'
        ON_HOLD = 'ON_HOLD', '保留'
    
    class PriorityChoices(models.TextChoices):
        HIGH = 'HIGH', '高'
        MEDIUM = 'MEDIUM', '中'
        LOW = 'LOW', '低'
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    task_number = models.CharField(max_length=20, verbose_name='タスク番号')
    title = models.CharField(max_length=200, verbose_name='タイトル')
    description = models.TextField(blank=True, verbose_name='説明')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.NOT_STARTED)
    priority = models.CharField(max_length=10, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM)
    
    # 日程
    planned_start_date = models.DateField(verbose_name='開始予定日')
    planned_end_date = models.DateField(verbose_name='終了予定日')
    actual_start_date = models.DateField(null=True, blank=True, verbose_name='開始実績日')
    actual_end_date = models.DateField(null=True, blank=True, verbose_name='終了実績日')
    
    # 工数
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='見積工数(h)')
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='実績工数(h)')
    progress_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='進捗率(%)')
    
    # WBS
    wbs_code = models.CharField(max_length=50, blank=True, verbose_name='WBSコード')
    level = models.IntegerField(default=0, verbose_name='階層レベル')
    
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
            while current:
                if current.id == self.id:
                    raise ValidationError('タスクの循環参照が検出されました')
                current = current.parent
```

#### TaskDependency（タスク依存関係）

```python
class TaskDependency(models.Model):
    class DependencyTypeChoices(models.TextChoices):
        FINISH_TO_START = 'FS', '終了-開始 (FS)'
        START_TO_START = 'SS', '開始-開始 (SS)'
        FINISH_TO_FINISH = 'FF', '終了-終了 (FF)'
        START_TO_FINISH = 'SF', '開始-終了 (SF)'
    
    predecessor = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='successors', verbose_name='前提タスク')
    successor = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='predecessors', verbose_name='後続タスク')
    dependency_type = models.CharField(max_length=2, choices=DependencyTypeChoices.choices, default=DependencyTypeChoices.FINISH_TO_START)
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
        
        # 循環参照チェック（簡易版）
        # 本番環境ではより厳密なグラフアルゴリズムを使用
        if TaskDependency.objects.filter(
            predecessor=self.successor, 
            successor=self.predecessor
        ).exists():
            raise ValidationError('循環依存が検出されました')
```

#### TaskComment（タスクコメント）

```python
class TaskComment(AbstractBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(verbose_name='コメント')
    
    class Meta:
        db_table = 'task_comments'
        verbose_name = 'タスクコメント'
        verbose_name_plural = 'タスクコメント'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task.task_number} - {self.user.display_name}"
```

#### Milestone（マイルストーン）

```python
class Milestone(AbstractBaseModel):
    class StatusChoices(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', '未達成'
        ACHIEVED = 'ACHIEVED', '達成'
        DELAYED = 'DELAYED', '遅延'
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    name = models.CharField(max_length=200, verbose_name='マイルストーン名')
    description = models.TextField(blank=True, verbose_name='説明')
    target_date = models.DateField(verbose_name='目標日')
    actual_date = models.DateField(null=True, blank=True, verbose_name='達成日')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.NOT_STARTED)
    criteria = models.TextField(blank=True, verbose_name='達成基準')
    order = models.IntegerField(default=0, verbose_name='表示順')
    
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
```

---

### 3.4 品質管理

#### Bug（バグ）

```python
class Bug(AbstractBaseModel):
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
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bugs')
    bug_number = models.CharField(max_length=20, verbose_name='バグ番号')
    title = models.CharField(max_length=200, verbose_name='タイトル')
    description = models.TextField(verbose_name='詳細説明')
    
    # 担当・報告
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_bugs')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bugs')
    
    # ステータス・優先度
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.NEW)
    priority = models.CharField(max_length=10, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM)
    severity = models.CharField(max_length=10, choices=SeverityChoices.choices, default=SeverityChoices.MEDIUM)
    
    # 分類
    category = models.CharField(max_length=50, blank=True, verbose_name='カテゴリ')
    module = models.CharField(max_length=100, blank=True, verbose_name='モジュール')
    
    # バージョン
    found_version = models.CharField(max_length=50, blank=True, verbose_name='発見バージョン')
    fixed_version = models.CharField(max_length=50, blank=True, verbose_name='修正バージョン')
    
    # 詳細情報
    reproduction_steps = models.TextField(blank=True, verbose_name='再現手順')
    environment = models.TextField(blank=True, verbose_name='環境情報')
    fix_description = models.TextField(blank=True, verbose_name='修正内容')
    test_result = models.TextField(blank=True, verbose_name='テスト結果')
    
    # 日程
    found_date = models.DateField(auto_now_add=True, verbose_name='発見日')
    fixed_date = models.DateField(null=True, blank=True, verbose_name='修正日')
    verified_date = models.DateField(null=True, blank=True, verbose_name='確認日')
    
    # 関連
    related_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_bugs')
    
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
```

#### BugComment（バグコメント）

```python
class BugComment(AbstractBaseModel):
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(verbose_name='コメント')
    
    class Meta:
        db_table = 'bug_comments'
        verbose_name = 'バグコメント'
        verbose_name_plural = 'バグコメント'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.bug.bug_number} - {self.user.display_name}"
```

#### TestCase（テストケース）

```python
class TestCase(AbstractBaseModel):
    class CategoryChoices(models.TextChoices):
        UNIT = 'UNIT', '単体テスト'
        INTEGRATION = 'INTEGRATION', '結合テスト'
        SYSTEM = 'SYSTEM', 'システムテスト'
        ACCEPTANCE = 'ACCEPTANCE', '受入テスト'
    
    class PriorityChoices(models.TextChoices):
        HIGH = 'HIGH', '高'
        MEDIUM = 'MEDIUM', '中'
        LOW = 'LOW', '低'
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='test_cases')
    test_case_number = models.CharField(max_length=20, verbose_name='テストケース番号')
    title = models.CharField(max_length=200, verbose_name='タイトル')
    category = models.CharField(max_length=20, choices=CategoryChoices.choices, default=CategoryChoices.UNIT)
    priority = models.CharField(max_length=10, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM)
    
    # テスト内容
    precondition = models.TextField(blank=True, verbose_name='前提条件')
    test_steps = models.TextField(verbose_name='テスト手順')
    expected_result = models.TextField(verbose_name='期待結果')
    
    # 分類
    target_function = models.CharField(max_length=100, blank=True, verbose_name='対象機能')
    module = models.CharField(max_length=100, blank=True, verbose_name='モジュール')
    
    # 関連
    related_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='test_cases')
    
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
```

#### TestExecution（テスト実行）

```python
class TestExecution(AbstractBaseModel):
    class ResultChoices(models.TextChoices):
        PASSED = 'PASSED', '成功'
        FAILED = 'FAILED', '失敗'
        NOT_EXECUTED = 'NOT_EXECUTED', '未実施'
        NOT_APPLICABLE = 'NOT_APPLICABLE', 'N/A'
    
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='executions')
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    executed_at = models.DateTimeField(auto_now_add=True, verbose_name='実行日時')
    result = models.CharField(max_length=20, choices=ResultChoices.choices, default=ResultChoices.NOT_EXECUTED)
    actual_result = models.TextField(blank=True, verbose_name='実績結果')
    execution_time = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='実行時間(分)')
    notes = models.TextField(blank=True, verbose_name='備考')
    
    # 関連バグ
    related_bug = models.ForeignKey(Bug, on_delete=models.SET_NULL, null=True, blank=True, related_name='test_executions')
    
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
```

#### QualityMetric（品質メトリクス）

```python
class QualityMetric(AbstractBaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='quality_metrics')
    metric_name = models.CharField(max_length=100, verbose_name='指標名')
    metric_type = models.CharField(max_length=50, verbose_name='指標タイプ')
    target_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='目標値')
    actual_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='実績値')
    unit = models.CharField(max_length=20, blank=True, verbose_name='単位')
    measured_at = models.DateField(verbose_name='測定日')
    notes = models.TextField(blank=True, verbose_name='備考')
    
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
```

---

### 3.5 レビュー管理

#### Review（レビュー）

```python
class Review(AbstractBaseModel):
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
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews')
    review_number = models.CharField(max_length=20, verbose_name='レビュー番号')
    title = models.CharField(max_length=200, verbose_name='タイトル')
    review_type = models.CharField(max_length=20, choices=TypeChoices.choices, default=TypeChoices.CODE)
    description = models.TextField(blank=True, verbose_name='説明')
    
    # 対象
    target_description = models.TextField(verbose_name='レビュー対象')
    target_document = models.FileField(upload_to='review_documents/', blank=True, null=True, verbose_name='対象ドキュメント')
    
    # 日時・場所
    scheduled_at = models.DateTimeField(verbose_name='実施予定日時')
    actual_start_at = models.DateTimeField(null=True, blank=True, verbose_name='開始日時')
    actual_end_at = models.DateTimeField(null=True, blank=True, verbose_name='終了日時')
    location = models.CharField(max_length=200, blank=True, verbose_name='場所')
    
    # ステータス
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PLANNED)
    conclusion = models.CharField(max_length=20, choices=ConclusionChoices.choices, default=ConclusionChoices.PENDING)
    
    # 議事録
    minutes = models.TextField(blank=True, verbose_name='議事録')
    decisions = models.TextField(blank=True, verbose_name='決定事項')
    issues = models.TextField(blank=True, verbose_name='課題')
    
    # 関連
    related_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    
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
```

#### ReviewParticipant（レビュー参加者）

```python
class ReviewParticipant(models.Model):
    class RoleChoices(models.TextChoices):
        MODERATOR = 'MODERATOR', 'モデレーター'
        REVIEWER = 'REVIEWER', 'レビュアー'
        AUTHOR = 'AUTHOR', '作成者'
        OBSERVER = 'OBSERVER', '参加者'
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.REVIEWER)
    attended = models.BooleanField(default=False, verbose_name='出席')
    
    class Meta:
        db_table = 'review_participants'
        verbose_name = 'レビュー参加者'
        verbose_name_plural = 'レビュー参加者'
        unique_together = [['review', 'user']]
    
    def __str__(self):
        return f"{self.review.review_number} - {self.user.display_name} ({self.role})"
```

#### ReviewIssue（指摘事項）

```python
class ReviewIssue(AbstractBaseModel):
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
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='issues')
    issue_number = models.CharField(max_length=20, verbose_name='指摘番号')
    description = models.TextField(verbose_name='指摘内容')
    severity = models.CharField(max_length=20, choices=SeverityChoices.choices, default=SeverityChoices.MAJOR)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.OPEN)
    
    # 担当
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_review_issues')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_review_issues')
    
    # 該当箇所
    location = models.CharField(max_length=200, blank=True, verbose_name='該当箇所')
    page_number = models.IntegerField(null=True, blank=True, verbose_name='ページ番号')
    line_number = models.IntegerField(null=True, blank=True, verbose_name='行番号')
    file_name = models.CharField(max_length=200, blank=True, verbose_name='ファイル名')
    
    # 対応
    response = models.TextField(blank=True, verbose_name='対応内容')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='対応完了日時')
    verifier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_review_issues')
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name='確認日時')
    
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
```

---

### 3.6 通知管理（Phase 2）

#### Notification（通知）

```python
class Notification(models.Model):
    class TypeChoices(models.TextChoices):
        TASK_ASSIGNED = 'TASK_ASSIGNED', 'タスク割り当て'
        TASK_DUE_SOON = 'TASK_DUE_SOON', 'タスク期限間近'
        TASK_DELAYED = 'TASK_DELAYED', 'タスク遅延'
        BUG_REGISTERED = 'BUG_REGISTERED', 'バグ登録'
        BUG_ASSIGNED = 'BUG_ASSIGNED', 'バグ割り当て'
        BUG_CRITICAL = 'BUG_CRITICAL', '致命的バグ'
        REVIEW_SCHEDULED = 'REVIEW_SCHEDULED', 'レビュー予定'
        REVIEW_COMPLETED = 'REVIEW_COMPLETED', 'レビュー完了'
        REVIEW_ISSUE_ASSIGNED = 'REVIEW_ISSUE_ASSIGNED', '指摘事項割り当て'
        MILESTONE_ACHIEVED = 'MILESTONE_ACHIEVED', 'マイルストーン達成'
        MILESTONE_DELAYED = 'MILESTONE_DELAYED', 'マイルストーン遅延'
        MENTION = 'MENTION', 'メンション'
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TypeChoices.choices)
    title = models.CharField(max_length=200, verbose_name='タイトル')
    message = models.TextField(verbose_name='メッセージ')
    link_url = models.CharField(max_length=500, blank=True, verbose_name='リンクURL')
    is_read = models.BooleanField(default=False, verbose_name='既読')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='既読日時')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 送信元プロジェクト
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    # 関連オブジェクト（Generic Foreign Key）
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        db_table = 'notifications'
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
            models.Index(fields=['project', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient.display_name} - {self.title}"
    
    @staticmethod
    def notify_project_managers(project, notification_type, title, message, content_object=None):
        """プロジェクトマネージャーに通知を送信"""
        pm_members = ProjectMember.objects.filter(
            project=project, 
            role='PM',
            is_deleted=False
        ).select_related('user')
        
        for pm_member in pm_members:
            Notification.objects.create(
                recipient=pm_member.user,
                project=project,
                notification_type=notification_type,
                title=title,
                message=message,
                content_object=content_object
            )
```

---

## 4. マスターデータ

### Category（カテゴリマスタ）

```python
class Category(models.Model):
    class CategoryTypeChoices(models.TextChoices):
        BUG = 'BUG', 'バグカテゴリ'
        TASK = 'TASK', 'タスクカテゴリ'
        MODULE = 'MODULE', 'モジュール'
    
    category_type = models.CharField(max_length=20, choices=CategoryTypeChoices.choices)
    name = models.CharField(max_length=100, verbose_name='名称')
    description = models.TextField(blank=True, verbose_name='説明')
    order = models.IntegerField(default=0, verbose_name='表示順')
    is_active = models.BooleanField(default=True, verbose_name='有効')
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'カテゴリ'
        verbose_name_plural = 'カテゴリ'
        ordering = ['category_type', 'order', 'name']
        unique_together = [['category_type', 'name']]
    
    def __str__(self):
        return f"{self.get_category_type_display()} - {self.name}"
```

---

## 5. インデックス戦略

### 5.1 複合インデックス
- `projects`: (status, start_date)
- `tasks`: (project, status), (assignee, status), (planned_start_date, planned_end_date)
- `bugs`: (project, status), (assignee, status), (priority, status)
- `reviews`: (project, status), (review_type, scheduled_at)
- `review_issues`: (review, status), (assignee, status)

### 5.2 ユニークインデックス
- `projects`: project_code
- `tasks`: (project, task_number)
- `bugs`: (project, bug_number)
- `test_cases`: (project, test_case_number)
- `reviews`: (project, review_number)

---

## 6. データ整合性制約

### 6.1 データベースレベル
- Foreign Key制約: ON_DELETE設定（CASCADE, SET_NULL, PROTECT）
- Unique制約: プロジェクト内での番号の一意性
- Check制約: 日付の妥当性（PostgreSQL）

### 6.2 アプリケーションレベル
- clean()メソッドでのバリデーション
- カスタムバリデーター
- シグナルでの整合性チェック

---

## 7. 監査とセキュリティ

### 7.1 変更履歴
- **django-simple-history**を使用して主要モデルの履歴を記録
- **対象モデル**: Project, Task, Bug, TestCase, Review, ReviewIssue
- **保存内容**: 全フィールドの変更前後の値、変更者、変更日時
- **保存期間**: 無期限（監査要件）
- **履歴の利用用途**:
  - 監査証跡
  - データ復元
  - 変更履歴の可視化
  - トラブルシューティング

**実装例**:
```python
from simple_history.models import HistoricalRecords

class Task(AbstractBaseModel):
    # ... fields ...
    history = HistoricalRecords()
```

### 7.2 論理削除
- is_deletedフラグによる論理削除
- カスタムマネージャーで削除済みデータを除外

```python
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

# 各モデルで使用
class Task(AbstractBaseModel):
    # ... fields ...
    objects = ActiveManager()
    all_objects = models.Manager()  # 削除済み含む
```

---

## 8. パフォーマンス最適化

### 8.1 select_related / prefetch_related
```python
# 効率的なクエリ例
tasks = Task.objects.select_related(
    'project', 'assignee', 'parent'
).prefetch_related(
    'subtasks', 'comments', 'predecessors'
).filter(project_id=project_id)
```

### 8.2 集計クエリ
```python
# プロジェクトの進捗率計算
from django.db.models import Avg, Count, Q

project_stats = Project.objects.annotate(
    total_tasks=Count('tasks'),
    completed_tasks=Count('tasks', filter=Q(tasks__status='COMPLETED')),
    avg_progress=Avg('tasks__progress_rate')
)
```

---

## 9. 次のステップ

1. **models.pyの実装**
   - Djangoアプリケーション構成の決定
   - モデルの実装
   
2. **マイグレーションファイル生成**
   - `python manage.py makemigrations`
   
3. **初期データ作成**
   - fixturesまたはmanagement commandsで初期データ投入
   
4. **Admin画面設定**
   - admin.pyの実装
   
5. **URLルーティング設計**
   - urls.pyの設計

---

## 10. 補足：モデル設計の確認ポイント

### 確認済み事項
✅ タスクとバグの関係: 別管理だが、related_taskで紐付け可能
✅ レビューとタスクの関係: 別管理だが、related_taskで紐付け可能
✅ 権限設計: モデルレベルでの権限フィールド定義完了
✅ 循環参照対策: clean()メソッドでバリデーション実装
✅ 削除時の整合性: CASCADE/SET_NULL/PROTECT適切に設定
✅ パフォーマンス: インデックス戦略定義

### 要検討事項
- ファイル添付機能の詳細仕様（サイズ制限、許可拡張子）
- Phase 2での詳細な権限制御実装
- 通知機能の詳細実装（Phase 2）

### 明確化済み事項
✅ **タスクとバグの関係**: 別管理。バグ修正作業をタスク化する場合はTask.related_bugで紐付け
✅ **レビューとタスクの関係**: レビュー実施自体はタスクとして管理せず、独立エンティティとして扱う
✅ **権限設計**: Phase 1では全ロールが全機能操作可能。Phase 2で詳細制御実装
✅ **通知タイミング**: プロジェクトマネージャー（PM）に主要イベントを通知
✅ **履歴管理**: 主要エンティティの全変更履歴を無期限保存（django-simple-history使用）
