# -*- coding: utf-8 -*-

# main file

# DB-Klasse importieren
from DbUtils import DbUtils
from Film import Film

# Reiner Testkram von Thomas - kann gerne wieder gelöscht werden
# Test der Datenbank-Klasse
db = DbUtils()

# --------------------------------------------------------------------
# Test von Thomas: Datenbank erzeugen und Abfrage ausgeben
# --------------------------------------------------------------------

# Löscht Datenbank und legt die Dabelle neu an
db.create_database()

# Test von Einträgen

# Film1 erzeugen und in DB speichern
film1 = Film()
film1.pfad = "c:\\erster_film.avi"
film1.name = "Dat is der erste Film"
film1.persist()

# Film2 erzeugen und in DB speichern
film2 = Film()
film2.pfad = "c:\\zweiter_film.mpeg"
film2.name = "Und der zweite Film"
film2.persist()

# Filme 1 und 2 ausgeben
fromdb1 = Film.get_by_id(film1.db_id)
print str(fromdb1.db_id) + " - " + fromdb1.name + ", " + fromdb1.pfad

fromdb2 = Film.get_by_id(film2.db_id)
print str(fromdb2.db_id) + " - " + fromdb2.name + ", " + fromdb2.pfad

# Film 2 löschen und testen, ob es funktioniert hat
fromdb2.delete()
deleted = Film.get_by_id(film2.db_id)
if deleted:
    print str(deleted.id) + deleted.name + ", " + deleted.pfad
else:
    print "Der Film mit der id %i wurde aus der Datenbank gelöscht!" % (film2.db_id)
