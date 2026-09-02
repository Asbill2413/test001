# -*- coding: utf-8 -*-
"""
ESG 数据库查询脚本（标准 PostgreSQL）
=====================================
用法:
    python esg_query.py "SELECT * FROM public.companies LIMIT 5"
    python esg_query.py -l            # 列出 public 下的所有表

依赖: pip install "psycopg[binary]"
"""
import sys

DB = dict(
    host="47.123.4.172",
    port=5432,
    dbname="esg_db",
    user="esg_readonly",
    password="EsgRead2026!",
    connect_timeout=15,
)


def main():
    import psycopg
    with psycopg.connect(**DB) as conn:
        with conn.cursor() as cur:
            if len(sys.argv) > 1 and sys.argv[1] in ("-l", "--list"):
                cur.execute("""SELECT table_name FROM information_schema.tables
                               WHERE table_schema='public' ORDER BY table_name""")
                rows = cur.fetchall()
                print(f"public 下的表 ({len(rows)}):")
                for (t,) in rows:
                    print("  " + t)
            else:
                sql = sys.argv[1] if len(sys.argv) > 1 else "SELECT current_database(), version()"
                cur.execute(sql)
                cols = [d[0] for d in cur.description] if cur.description else []
                print(" | ".join(cols))
                print("-" * 60)
                n = 0
                for row in cur:
                    print(" | ".join("" if v is None else str(v) for v in row))
                    n += 1
                    if n >= 200:
                        print("...(仅显示前 200 行)")
                        break
                print(f"共 {n} 行")


if __name__ == "__main__":
    main()
