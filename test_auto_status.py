"""
自動ステータス更新機能のテスト
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tasks.models import Task
from datetime import date

print("=" * 60)
print("自動ステータス更新機能テスト")
print("=" * 60)

# テスト1: 実績開始日を設定
print("\n【テスト1: 実績開始日を設定】")
task = Task.objects.filter(status='NOT_STARTED').first()
if task:
    print(f"タスク: {task.task_number} - {task.title}")
    print(f"変更前: ステータス={task.get_status_display()}, 進捗率={task.progress_rate}")
    
    task.actual_start_date = date(2025, 1, 10)
    task.save()
    
    print(f"変更後: ステータス={task.get_status_display()}, 進捗率={task.progress_rate}")
    print(f"✅ 実績開始日を設定 → ステータスが「進行中」になりました" if task.status == 'IN_PROGRESS' else "❌ 失敗")
else:
    print("未着手のタスクが見つかりません")

# テスト2: 実績終了日を設定
print("\n【テスト2: 実績終了日を設定】")
task = Task.objects.filter(status='IN_PROGRESS').first()
if task:
    print(f"タスク: {task.task_number} - {task.title}")
    print(f"変更前: ステータス={task.get_status_display()}, 進捗率={task.progress_rate}")
    
    if not task.actual_start_date:
        task.actual_start_date = date(2025, 1, 10)
    task.actual_end_date = date(2025, 1, 20)
    task.save()
    
    print(f"変更後: ステータス={task.get_status_display()}, 進捗率={task.progress_rate}")
    print(f"✅ 実績終了日を設定 → ステータスが「完了」、進捗率が100%になりました" if task.status == 'COMPLETED' and task.progress_rate == 100 else "❌ 失敗")
else:
    print("進行中のタスクが見つかりません")

# テスト3: 実績終了日を削除
print("\n【テスト3: 実績終了日を削除】")
task = Task.objects.filter(status='COMPLETED').first()
if task:
    print(f"タスク: {task.task_number} - {task.title}")
    print(f"変更前: ステータス={task.get_status_display()}, 実績開始日={task.actual_start_date}, 実績終了日={task.actual_end_date}")
    
    task.actual_end_date = None
    task.save()
    
    print(f"変更後: ステータス={task.get_status_display()}, 実績終了日={task.actual_end_date}")
    print(f"✅ 実績終了日を削除 → ステータスが「進行中」に戻りました" if task.status == 'IN_PROGRESS' else "❌ 失敗")
else:
    print("完了したタスクが見つかりません")

print("\n" + "=" * 60)
print("テスト完了")
print("=" * 60)
