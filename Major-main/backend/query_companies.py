import sqlite3, json, sys

DB = 'cloud_broker.db'
try:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT * FROM companies')
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    results = [dict(zip(cols, row)) for row in rows]
    print(json.dumps(results, indent=2, default=str))
except Exception as e:
    print('ERROR:', e)
    sys.exit(1)
finally:
    try:
        conn.close()
    except:
        pass
