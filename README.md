# プロジェクト管理システム

システム開発プロジェクトのスケジュール管理、品質管理、レビュー管理を行うDjangoベースのプロジェクト管理システムです。

## 機能

- **プロジェクト管理**: プロジェクトの作成、メンバー管理、マイルストーン管理
- **タスク管理**: タスクの作成、割り当て、進捗管理、ガントチャート、カレンダー表示
- **品質管理**: バグ管理、品質メトリクス
- **レビュー管理**: レビュー実施、指摘管理
- **ダッシュボード**: プロジェクト全体の状況把握

## セットアップ

### 前提条件

- Python 3.13+
- PostgreSQL 13+

### データベース設定

PostgreSQLに以下のスキーマを作成してください：

```sql
CREATE SCHEMA prjMng;
```

### インストール

1. 仮想環境を作成・有効化

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

3. 環境変数を設定（.env ファイルを作成）

```
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=pass
DB_HOST=localhost
DB_PORT=5432
DB_SCHEMA=prjMng
SECRET_KEY=your-secret-key-here
DEBUG=True
```

4. マイグレーション実行

```bash
python manage.py migrate
```

5. スーパーユーザー作成

```bash
python create_superuser.py
```

6. テストデータ投入（オプション）

```bash
python create_test_data.py
```

7. 開発サーバー起動

```bash
python manage.py runserver
```

ブラウザで http://127.0.0.1:8000/ にアクセスしてください。

## 使用技術

- Django 4.2.7
- PostgreSQL
- Bootstrap 5
- FullCalendar
- dhtmlxGantt
- django-simple-history

## プロジェクト構成

```
prjMng/
├── apps/
│   ├── accounts/      # ユーザー・組織管理
│   ├── projects/      # プロジェクト管理
│   ├── tasks/         # タスク管理
│   ├── quality/       # 品質管理
│   └── reviews/       # レビュー管理
├── config/            # Django設定
├── templates/         # 共通テンプレート
├── static/            # 静的ファイル
└── manage.py
```

## ライセンス

MIT License
