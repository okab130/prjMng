import psycopg

# データベース接続
conn = psycopg.connect(
    host='localhost',
    port=5432,
    dbname='postgres',
    user='postgres',
    password='pass'
)

# スキーマ作成
with conn.cursor() as cur:
    cur.execute("CREATE SCHEMA IF NOT EXISTS prjMng;")
    conn.commit()
    print("Schema 'prjMng' created successfully!")

conn.close()
