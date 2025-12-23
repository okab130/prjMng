from django.core.management import execute_from_command_line
import sys

# スーパーユーザー作成スクリプト
from apps.accounts.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        employee_id='EMP001',
        display_name='管理者',
        role='ADMIN'
    )
    print('スーパーユーザーが作成されました')
    print('Username: admin')
    print('Password: admin123')
else:
    print('スーパーユーザーは既に存在します')
