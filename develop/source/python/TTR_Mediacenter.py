# -*- coding: utf-8 -*-

# main file

# DB-Klasse importieren
from DbUtils import DbUtils
from Film import Film
from Genre import Genre
from FileType import FileType

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# nur zum Test
import hashlib

# Reiner Testkram von Thomas - kann gerne wieder gelöscht werden
# Test der Datenbank-Klasse
db = DbUtils()

# --------------------------------------------------------------------
# Test von Thomas: Datenbank erzeugen und Abfrage ausgeben
# --------------------------------------------------------------------

# Löscht Datenbank und legt die Dabelle neu an
db.create_database()

# Test von Einträgen und dem Cache

# Film muss 1x instanziiert werden, damit der Cache in der Klasse initialisiert wird
# Sieht nicht so schön aus, weil eigentlich statisches Feld, aber funktioniert
filmcache = Film.get_cache()

# Film1 erzeugen und in DB speichern
film1 = Film()
film1.set_pfad("c:\\erster_film.avi")
film1.set_name("Dat is der erste Film")
checksum1 = hashlib.md5()
checksum1.update("Film1")
film1.set_checksum(checksum1.hexdigest())
film1.set_genre(Genre.get_cache().get_by_id(1))
film1.set_filetype(FileType.get_cache().get_by_id(1))
filmcache.persist(film1)

# Film2 erzeugen und in DB speichern
film2 = Film()
film2.set_pfad("c:\\zweiter_film.mpeg")
film2.set_name("Und der zweite Film")
checksum2 = hashlib.md5()
checksum2.update("film2")
film2.set_checksum(checksum2.hexdigest())
film2.set_genre(Genre.get_cache().get_by_id(2))
film2.set_filetype(FileType.get_cache().get_by_id(2))
filmcache.persist(film2)

# Filme 1 und 2 ausgeben
fromdb1 = filmcache.get_by_id(film1.get_db_id())
print(str(fromdb1.get_db_id()) + " - " + fromdb1.get_name() + ", " + fromdb1.get_pfad() + ", " + fromdb1.get_genre().get_name() + ", " + fromdb1.get_filetype().get_name() + ", " + str(fromdb1.get_checksum()))

fromdb2 = filmcache.get_by_id(film2.get_db_id())
print(str(fromdb2.get_db_id()) + " - " + fromdb2.get_name() + ", " + fromdb2.get_pfad() + ", " + fromdb2.get_genre().get_name() + ", " + fromdb2.get_filetype().get_name() + ", " + str(fromdb2.get_checksum()))
print("ID Film (original):  ")
print(fromdb2)

# ------ Test ob das gleiche Objekt aus dem Cache geholt wird ------

fromdb2a = filmcache.get_by_id(film2.get_db_id())
print("ID Film (aus Cache): ")
print(fromdb2a)

fromdb2b = Film.get_by_id(film2.get_db_id())
print "ID Film (aus DB):    "
print fromdb2b

# Film 2 löschen und testen, ob es funktioniert hat
print filmcache.instances
filmcache.delete(fromdb2)
deleted = filmcache.get_by_id(film2.get_db_id())
if deleted:
    print str(deleted.id) + deleted.get_name() + ", " + deleted.get_pfad()
else:
    print "Der Film mit der id %i wurde aus der Datenbank gelöscht!" % (film2.get_db_id())
