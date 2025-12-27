# Generated manually for data migration

from django.db import migrations


def create_default_categories(apps, schema_editor):
    """既存タスクにデフォルト分類を設定"""
    Project = apps.get_model('projects', 'Project')
    SystemCategory = apps.get_model('tasks', 'SystemCategory')
    MajorCategory = apps.get_model('tasks', 'MajorCategory')
    MinorCategory = apps.get_model('tasks', 'MinorCategory')
    Task = apps.get_model('tasks', 'Task')
    
    # 各プロジェクトにデフォルト分類を作成
    for project in Project.objects.filter(is_deleted=False):
        # デフォルトシステム作成
        system, created = SystemCategory.objects.get_or_create(
            project=project,
            code='DEFAULT',
            defaults={
                'name': '未分類',
                'description': '既存タスク用のデフォルト分類',
                'order': 999,
                'is_deleted': False
            }
        )
        
        # デフォルト大分類作成
        major, created = MajorCategory.objects.get_or_create(
            system_category=system,
            code='DEFAULT',
            defaults={
                'name': '未分類',
                'description': '既存タスク用のデフォルト分類',
                'order': 999,
                'is_deleted': False
            }
        )
        
        # デフォルト中分類作成
        minor, created = MinorCategory.objects.get_or_create(
            major_category=major,
            code='DEFAULT',
            defaults={
                'name': '未分類',
                'description': '既存タスク用のデフォルト分類',
                'order': 999,
                'is_deleted': False
            }
        )
        
        # 既存タスク（分類が未設定）を未分類に設定
        updated_count = Task.objects.filter(
            project=project,
            system_category__isnull=True
        ).update(
            system_category=system,
            major_category=major,
            minor_category=minor
        )
        
        print(f"プロジェクト '{project.name}' にデフォルト分類を作成し、{updated_count}件のタスクを移行しました。")


def reverse_migration(apps, schema_editor):
    """ロールバック処理（デフォルト分類を削除）"""
    SystemCategory = apps.get_model('tasks', 'SystemCategory')
    
    # DEFAULTコードの分類を削除（CASCADE で大分類・中分類も削除される）
    deleted_count, _ = SystemCategory.objects.filter(code='DEFAULT').delete()
    print(f"{deleted_count}件のデフォルト分類を削除しました。")


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_add_category_models'),
    ]

    operations = [
        migrations.RunPython(create_default_categories, reverse_migration),
    ]
