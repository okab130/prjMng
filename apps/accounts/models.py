from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords


class User(AbstractUser):
    """カスタムユーザーモデル"""
    
    class RoleChoices(models.TextChoices):
        ADMIN = 'ADMIN', '管理者'
        PM = 'PM', 'プロジェクトマネージャー'
        LEADER = 'LEADER', 'リーダー'
        MEMBER = 'MEMBER', 'メンバー'
        VIEWER = 'VIEWER', '閲覧者'
    
    employee_id = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='社員番号'
    )
    display_name = models.CharField(
        max_length=100, 
        verbose_name='表示名'
    )
    department = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='所属部署'
    )
    role = models.CharField(
        max_length=10, 
        choices=RoleChoices.choices, 
        default=RoleChoices.MEMBER,
        verbose_name='ロール'
    )
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name='電話番号'
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True, 
        verbose_name='アバター'
    )
    last_login_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='最終ログイン'
    )
    
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'
        ordering = ['employee_id']
    
    def __str__(self):
        return f"{self.display_name} ({self.employee_id})"
