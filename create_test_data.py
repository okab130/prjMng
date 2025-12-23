"""
テストデータ作成スクリプト
"""
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.projects.models import Project, ProjectMember, Milestone
from apps.tasks.models import Task
from apps.quality.models import Bug, TestCase
from apps.reviews.models import Review, ReviewParticipant

def create_test_data():
    """テストデータを作成"""
    
    # ユーザー作成
    print("ユーザー作成中...")
    users = []
    for i in range(1, 6):
        user, created = User.objects.get_or_create(
            username=f'user{i}',
            defaults={
                'employee_id': f'EMP{i:03d}',
                'display_name': f'テストユーザー{i}',
                'email': f'user{i}@example.com',
                'department': '開発部',
                'role': User.RoleChoices.MEMBER
            }
        )
        if created:
            user.set_password('password123')
            user.save()
        users.append(user)
    print(f"{len(users)}人のユーザーを作成しました")
    
    # プロジェクト作成
    print("\nプロジェクト作成中...")
    project, created = Project.objects.get_or_create(
        project_code='PRJ001',
        defaults={
            'name': 'プロジェクト管理システム開発',
            'description': 'スケジュール管理、品質管理、レビュー管理を統合したシステム',
            'status': Project.StatusChoices.IN_PROGRESS,
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=180),
            'progress_rate': 25.0,
            'created_by': users[0],
            'updated_by': users[0]
        }
    )
    print(f"プロジェクト '{project.name}' を作成しました")
    
    # プロジェクトメンバー追加
    print("\nプロジェクトメンバー追加中...")
    roles = [
        ProjectMember.RoleChoices.PM,
        ProjectMember.RoleChoices.LEADER,
        ProjectMember.RoleChoices.MEMBER,
        ProjectMember.RoleChoices.MEMBER,
        ProjectMember.RoleChoices.VIEWER
    ]
    for user, role in zip(users, roles):
        ProjectMember.objects.get_or_create(
            project=project,
            user=user,
            defaults={
                'role': role,
                'created_by': users[0]
            }
        )
    print(f"{len(users)}人のメンバーを追加しました")
    
    # マイルストーン作成
    print("\nマイルストーン作成中...")
    milestones = [
        {'name': '要件定義完了', 'order': 1, 'days': 30},
        {'name': '基本設計完了', 'order': 2, 'days': 60},
        {'name': '詳細設計完了', 'order': 3, 'days': 90},
        {'name': '開発完了', 'order': 4, 'days': 150},
        {'name': 'テスト完了', 'order': 5, 'days': 180},
    ]
    for ms_data in milestones:
        Milestone.objects.get_or_create(
            project=project,
            name=ms_data['name'],
            defaults={
                'target_date': timezone.now().date() + timedelta(days=ms_data['days']),
                'status': Milestone.StatusChoices.NOT_STARTED,
                'order': ms_data['order'],
                'created_by': users[0]
            }
        )
    print(f"{len(milestones)}件のマイルストーンを作成しました")
    
    # タスク作成
    print("\nタスク作成中...")
    tasks_data = [
        {'number': 'T001', 'title': '要件定義書作成', 'priority': Task.PriorityChoices.HIGH, 'days': 10},
        {'number': 'T002', 'title': 'モデル設計', 'priority': Task.PriorityChoices.HIGH, 'days': 15},
        {'number': 'T003', 'title': '画面設計', 'priority': Task.PriorityChoices.MEDIUM, 'days': 20},
        {'number': 'T004', 'title': 'データベース構築', 'priority': Task.PriorityChoices.HIGH, 'days': 25},
        {'number': 'T005', 'title': '機能実装', 'priority': Task.PriorityChoices.HIGH, 'days': 60},
    ]
    for task_data in tasks_data:
        Task.objects.get_or_create(
            project=project,
            task_number=task_data['number'],
            defaults={
                'title': task_data['title'],
                'assignee': users[1],
                'status': Task.StatusChoices.IN_PROGRESS,
                'priority': task_data['priority'],
                'planned_start_date': timezone.now().date(),
                'planned_end_date': timezone.now().date() + timedelta(days=task_data['days']),
                'estimated_hours': 40,
                'progress_rate': 30.0,
                'created_by': users[0]
            }
        )
    print(f"{len(tasks_data)}件のタスクを作成しました")
    
    # バグ作成
    print("\nバグ作成中...")
    bugs_data = [
        {'number': 'BUG001', 'title': 'ログイン画面でエラーが発生', 'priority': Bug.PriorityChoices.HIGH},
        {'number': 'BUG002', 'title': 'タスク一覧の表示が遅い', 'priority': Bug.PriorityChoices.MEDIUM},
        {'number': 'BUG003', 'title': 'CSVエクスポートが機能しない', 'priority': Bug.PriorityChoices.LOW},
    ]
    for bug_data in bugs_data:
        Bug.objects.get_or_create(
            project=project,
            bug_number=bug_data['number'],
            defaults={
                'title': bug_data['title'],
                'description': f'{bug_data["title"]}の詳細説明',
                'reporter': users[2],
                'assignee': users[1],
                'status': Bug.StatusChoices.NEW,
                'priority': bug_data['priority'],
                'severity': Bug.SeverityChoices.MEDIUM,
                'reproduction_steps': '1. システムにログイン\n2. 該当機能を実行\n3. エラー発生',
                'created_by': users[2]
            }
        )
    print(f"{len(bugs_data)}件のバグを作成しました")
    
    # テストケース作成
    print("\nテストケース作成中...")
    testcases_data = [
        {'number': 'TC001', 'title': 'ログイン機能テスト', 'category': TestCase.CategoryChoices.UNIT},
        {'number': 'TC002', 'title': 'タスク登録テスト', 'category': TestCase.CategoryChoices.INTEGRATION},
        {'number': 'TC003', 'title': 'バグ管理テスト', 'category': TestCase.CategoryChoices.SYSTEM'},
    ]
    for tc_data in testcases_data:
        TestCase.objects.get_or_create(
            project=project,
            test_case_number=tc_data['number'],
            defaults={
                'title': tc_data['title'],
                'category': tc_data['category'],
                'priority': TestCase.PriorityChoices.HIGH,
                'test_steps': '1. 前提条件を確認\n2. テスト実行\n3. 結果確認',
                'expected_result': '期待通りに動作すること',
                'created_by': users[3]
            }
        )
    print(f"{len(testcases_data)}件のテストケースを作成しました")
    
    # レビュー作成
    print("\nレビュー作成中...")
    review, created = Review.objects.get_or_create(
        project=project,
        review_number='REV001',
        defaults={
            'title': '設計レビュー',
            'review_type': Review.TypeChoices.DESIGN,
            'target_description': 'データベース設計書',
            'scheduled_at': timezone.now() + timedelta(days=7),
            'status': Review.StatusChoices.PLANNED,
            'conclusion': Review.ConclusionChoices.PENDING,
            'created_by': users[0]
        }
    )
    if created:
        # レビュー参加者追加
        for user in users[:4]:
            ReviewParticipant.objects.get_or_create(
                review=review,
                user=user,
                defaults={
                    'role': ReviewParticipant.RoleChoices.REVIEWER
                }
            )
    print("レビューを作成しました")
    
    print("\n" + "="*50)
    print("テストデータの作成が完了しました！")
    print(f"プロジェクト: {Project.objects.count()}件")
    print(f"ユーザー: {User.objects.count()}件")
    print(f"タスク: {Task.objects.count()}件")
    print(f"バグ: {Bug.objects.count()}件")
    print(f"テストケース: {TestCase.objects.count()}件")
    print(f"レビュー: {Review.objects.count()}件")
    print("="*50)

if __name__ == '__main__':
    import django
    django.setup()
    create_test_data()
