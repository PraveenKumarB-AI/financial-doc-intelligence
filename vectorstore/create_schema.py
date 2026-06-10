from vectorstore.database import get_connection

conn = get_connection()

cursor = conn.cursor()

with open(
    "vectorstore/schema.sql",
    "r"
) as f:
    cursor.execute(f.read())

conn.commit()

cursor.close()
conn.close()

print("Schema Created")
