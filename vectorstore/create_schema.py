from vectorstore.database import get_connection

conn = get_connection()
cur = conn.cursor()

with open("vectorstore/schema.sql") as f:
    cur.execute(f.read())

conn.commit()
cur.close()
conn.close()

print("Schema created successfully!")