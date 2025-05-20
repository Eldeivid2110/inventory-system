import sqlite3

conn = sqlite3.connect("inventorydb.db")
cursor = conn.cursor()
cursor.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", ("admin", "1234"))
conn.commit()
conn.close()