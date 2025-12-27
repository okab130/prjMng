# Generated manually for task number migration

from django.db import migrations


def convert_task_numbers(apps, schema_editor):
    """既存のタスク番号を3桁数字に変換"""
    Task = apps.get_model('tasks', 'Task')
    Project = apps.get_model('projects', 'Project')
    
    for project in Project.objects.filter(is_deleted=False):
        # プロジェクトごとにタスクを取得
        tasks = Task.objects.filter(
            project=project,
            is_deleted=False
        ).order_by('created_at')
        
        # 001から連番で振り直し
        for index, task in enumerate(tasks, start=1):
            old_number = task.task_number
            new_number = f"{index:03d}"
            task.task_number = new_number
            task.save()
            print(f"プロジェクト '{project.name}': {old_number} → {new_number}")
        
        print(f"プロジェクト '{project.name}': {tasks.count()}件のタスク番号を変換しました")


def reverse_migration(apps, schema_editor):
    """ロールバック（元に戻すことはできません）"""
    print("警告: タスク番号の元の値は復元できません")


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_migrate_existing_tasks'),
    ]

    operations = [
        migrations.RunPython(convert_task_numbers, reverse_migration),
    ]
