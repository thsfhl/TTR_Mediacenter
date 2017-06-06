# -*- coding: utf-8 -*-

# main file

# DB-Klasse importieren
from DbUtils import DbUtils

# Reiner Testkram von Thomas - kann gerne wieder gelöscht werden
# Test der Datenbank-Klasse
db = DbUtils()

# --------------------------------------------------------------------
# Test von Thomas: Datenbank erzeugen und Abfrage ausgeben
# --------------------------------------------------------------------

# Löscht Datenbank und legt die Dabelle neu an
db.create_database()

# Test von Einträgen, später über Entity-Manager erledigen

cur = db.get_cursor()

filme = (
    ("Fear and Loathing in Las Vegas", "fear_and_loathing.avi"),
    ("Star Wars IV", "star_wars_4.mpeg")
    )

# Filme aus Liste einfügen
cur.executemany("INSERT INTO Filme(name, pfad) VALUES(?,?)", filme)

# Query tatsächlich ausführen
db.get_connection().commit()

for row in cur.execute("SELECT * FROM Filme"):
    print row
