import sys, re, duckdb
FACT, SQL = sys.argv[1], sys.argv[2]
con = duckdb.connect()
con.execute(f"CREATE VIEW f AS SELECT * FROM '{FACT}'")
text = open(SQL).read()
blocks = re.split(r"\n(?=-- Q\d+\.)", text)
for b in blocks:
    m = re.search(r"-- name: (\w+)", b)
    if not m: continue
    sql = "\n".join(l for l in b.splitlines() if not l.strip().startswith("--"))
    print("\n===== " + m.group(1).upper() + " =====")
    print(con.execute(sql).df().to_string(index=False))
