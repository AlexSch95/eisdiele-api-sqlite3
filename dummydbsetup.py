import sqlite3

con = sqlite3.connect("eisdiele.db")
cur = con.cursor()

cur.execute(f"""INSERT INTO flavours (name, type, price_per_serving)
VALUES
("schokolade", "milch", 1.5),
("vanille", "milch", 1.5),
("zitrone", "frucht", 1.3);""")
con.commit()