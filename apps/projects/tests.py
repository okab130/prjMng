from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.projects.models import Project, ProjectMember


class UserModelTest(TestCase):
    """Userモデルのテスト"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP001',
            display_name='テストユーザー',
            role='MEMBER'
        )
    
    def test_user_creation(self):
        """ユーザーが正しく作成されること"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.employee_id, 'EMP001')
        self.assertEqual(self.user.display_name, 'テストユーザー')
        self.assertEqual(self.user.role, 'MEMBER')
    
    def test_user_str(self):
        """__str__メソッドが正しく動作すること"""
        expected = 'テストユーザー (EMP001)'
        self.assertEqual(str(self.user), expected)


class ProjectModelTest(TestCase):
    """Projectモデルのテスト"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP001',
            display_name='テストユーザー'
        )
        self.project = Project.objects.create(
            project_code='PRJ001',
            name='テストプロジェクト',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=90),
            status='IN_PROGRESS',
            created_by=self.user
        )
    
    def test_project_creation(self):
        """プロジェクトが正しく作成されること"""
        self.assertEqual(self.project.project_code, 'PRJ001')
        self.assertEqual(self.project.name, 'テストプロジェクト')
        self.assertEqual(self.project.status, 'IN_PROGRESS')
    
    def test_project_str(self):
        """__str__メソッドが正しく動作すること"""
        expected = 'PRJ001 - テストプロジェクト'
        self.assertEqual(str(self.project), expected)
    
    def test_project_member_relationship(self):
        """プロジェクトメンバーの関連が正しく動作すること"""
        ProjectMember.objects.create(
            project=self.project,
            user=self.user,
            role='PM',
            created_by=self.user
        )
        self.assertEqual(self.project.members.count(), 1)
        member = self.project.members.first()
        self.assertEqual(member.user, self.user)
        self.assertEqual(member.role, 'PM')
