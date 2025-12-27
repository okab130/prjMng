"""
マスタデータ登録スクリプト
システム名、大分類、中分類のテストデータを作成
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.projects.models import Project
from apps.tasks.models import SystemCategory, MajorCategory, MinorCategory

def create_test_categories():
    """テスト用の分類マスタを作成"""
    
    # プロジェクトを取得
    project = Project.objects.first()
    
    if not project:
        print("プロジェクトが存在しません")
        return
    
    print(f"プロジェクト: {project.name}")
    print("=" * 60)
    
    # システム名の作成
    systems_data = [
        {'code': 'WEB', 'name': 'Webシステム', 'description': 'Webアプリケーション', 'order': 1},
        {'code': 'MOBILE', 'name': 'モバイルアプリ', 'description': 'iOS/Androidアプリ', 'order': 2},
        {'code': 'API', 'name': 'APIサーバー', 'description': 'バックエンドAPI', 'order': 3},
        {'code': 'ADMIN', 'name': '管理画面', 'description': '管理者用システム', 'order': 4},
    ]
    
    for sys_data in systems_data:
        system, created = SystemCategory.objects.get_or_create(
            project=project,
            code=sys_data['code'],
            defaults={
                'name': sys_data['name'],
                'description': sys_data['description'],
                'order': sys_data['order']
            }
        )
        if created:
            print(f"✓ システム名作成: {system.code} - {system.name}")
        else:
            print(f"  システム名存在: {system.code} - {system.name}")
    
    print()
    
    # 大分類の作成
    major_data = {
        'WEB': [
            {'code': 'AUTH', 'name': '認証・認可', 'description': 'ログイン・権限管理', 'order': 1},
            {'code': 'ORDER', 'name': '注文管理', 'description': '注文処理機能', 'order': 2},
            {'code': 'MENU', 'name': 'メニュー管理', 'description': 'メニュー登録・編集', 'order': 3},
            {'code': 'UI', 'name': 'UI/UX', 'description': '画面デザイン', 'order': 4},
        ],
        'MOBILE': [
            {'code': 'UI', 'name': 'UI実装', 'description': 'モバイルUI', 'order': 1},
            {'code': 'FUNC', 'name': '機能実装', 'description': 'アプリ機能', 'order': 2},
            {'code': 'TEST', 'name': 'テスト', 'description': '動作確認', 'order': 3},
        ],
        'API': [
            {'code': 'AUTH', 'name': '認証API', 'description': '認証エンドポイント', 'order': 1},
            {'code': 'ORDER', 'name': '注文API', 'description': '注文処理', 'order': 2},
            {'code': 'MENU', 'name': 'メニューAPI', 'description': 'メニュー情報', 'order': 3},
            {'code': 'PAYMENT', 'name': '決済API', 'description': '決済処理', 'order': 4},
        ],
        'ADMIN': [
            {'code': 'MASTER', 'name': 'マスタ管理', 'description': 'マスタデータ', 'order': 1},
            {'code': 'REPORT', 'name': 'レポート', 'description': '集計・分析', 'order': 2},
            {'code': 'SETTING', 'name': '設定', 'description': 'システム設定', 'order': 3},
        ],
    }
    
    for sys_code, majors in major_data.items():
        system = SystemCategory.objects.get(project=project, code=sys_code)
        for major_item in majors:
            major, created = MajorCategory.objects.get_or_create(
                system_category=system,
                code=major_item['code'],
                defaults={
                    'name': major_item['name'],
                    'description': major_item['description'],
                    'order': major_item['order']
                }
            )
            if created:
                print(f"✓ 大分類作成: {system.code}/{major.code} - {major.name}")
    
    print()
    
    # 中分類の作成
    minor_data = {
        ('WEB', 'AUTH'): [
            {'code': 'LOGIN', 'name': 'ログイン機能', 'order': 1},
            {'code': 'LOGOUT', 'name': 'ログアウト機能', 'order': 2},
            {'code': 'PASSWD', 'name': 'パスワード管理', 'order': 3},
        ],
        ('WEB', 'ORDER'): [
            {'code': 'CART', 'name': 'カート機能', 'order': 1},
            {'code': 'CONFIRM', 'name': '注文確認', 'order': 2},
            {'code': 'HISTORY', 'name': '注文履歴', 'order': 3},
        ],
        ('WEB', 'MENU'): [
            {'code': 'LIST', 'name': 'メニュー一覧', 'order': 1},
            {'code': 'DETAIL', 'name': 'メニュー詳細', 'order': 2},
            {'code': 'SEARCH', 'name': 'メニュー検索', 'order': 3},
        ],
        ('API', 'AUTH'): [
            {'code': 'TOKEN', 'name': 'トークン発行', 'order': 1},
            {'code': 'REFRESH', 'name': 'トークン更新', 'order': 2},
            {'code': 'VERIFY', 'name': 'トークン検証', 'order': 3},
        ],
        ('API', 'ORDER'): [
            {'code': 'CREATE', 'name': '注文作成', 'order': 1},
            {'code': 'UPDATE', 'name': '注文更新', 'order': 2},
            {'code': 'CANCEL', 'name': '注文キャンセル', 'order': 3},
        ],
    }
    
    for (sys_code, major_code), minors in minor_data.items():
        system = SystemCategory.objects.get(project=project, code=sys_code)
        major = MajorCategory.objects.get(system_category=system, code=major_code)
        for minor_item in minors:
            minor, created = MinorCategory.objects.get_or_create(
                major_category=major,
                code=minor_item['code'],
                defaults={
                    'name': minor_item['name'],
                    'order': minor_item['order']
                }
            )
            if created:
                print(f"✓ 中分類作成: {system.code}/{major.code}/{minor.code} - {minor.name}")
    
    print()
    print("=" * 60)
    print("マスタデータの作成が完了しました")
    print()
    
    # 作成結果の集計
    total_systems = SystemCategory.objects.filter(project=project).count()
    total_majors = MajorCategory.objects.filter(system_category__project=project).count()
    total_minors = MinorCategory.objects.filter(major_category__system_category__project=project).count()
    
    print(f"システム名: {total_systems}件")
    print(f"大分類: {total_majors}件")
    print(f"中分類: {total_minors}件")

if __name__ == '__main__':
    create_test_categories()
