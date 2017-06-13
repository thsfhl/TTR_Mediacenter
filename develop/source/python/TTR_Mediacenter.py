# -*- coding: utf-8 -*-

# main file

import sys
import os
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
import argparse

# DB-Klasse importieren
from database.DbUtils import DbUtils
from database.FileType import FileType
from database.Film import Film
from database.Genre import Genre
from FilmCrawler import FilmCrawler

from gui.TTRFileChooser import TTRFileChooser

# nur zum Test
import hashlib

def addFilm(id, titel, pfad, filename, genre_id, filetype_id):
    # Film1 erzeugen und in DB speichern
    film = Film()
    film.set_pfad(pfad)
    film.set_titel(titel)
    film.set_filename(filename)
    md5 = hashlib.md5()
    md5.update("Bam")
    film.set_checksum(md5.hexdigest())
    film.set_genre(Genre.get_by_id(genre_id))
    film.set_filetype(FileType.get_by_id(filetype_id))
    Film.persist(film)
    return film

def dbTests():
    # Reiner Testkram von Thomas - kann gerne wieder gelöscht werden
    # Test der Datenbank-Klasse
    db = DbUtils()

    # --------------------------------------------------------------------
    # Test von Thomas: Datenbank erzeugen und Abfrage ausgeben
    # --------------------------------------------------------------------

    # Löscht Datenbank und legt die Dabelle neu an
    db.create_database()

    # Test von Einträgen und dem Cache

    pfad = "c:\ordnername\\"
    filename = "erster_film.avi"
    titel = "Dat is der erste Film"
    id = 1
    film1 = addFilm(id, titel, pfad, filename, id, id)

    filename = "zweiter_film.mpeg"
    titel = "Dat ist der zweite Film"
    id = 2
    # Film2 erzeugen und in DB speichern
    film2 = addFilm(id, titel, pfad, filename, id, id)

    # Filme 1 und 2 ausgeben
    fromdb1 = Film.get_by_id(film1.get_db_id())
    print(str(fromdb1.get_db_id()) + " - " + fromdb1.get_titel() + ", " + fromdb1.get_pfad() + ", " + fromdb1.get_genre().get_name() + ", " + fromdb1.get_filetype().get_name() + ", " + str(fromdb1.get_checksum()))

    fromdb2 = Film.get_by_id(film2.get_db_id())
    print(str(fromdb2.get_db_id()) + " - " + fromdb2.get_titel() + ", " + fromdb2.get_pfad() + ", " + fromdb2.get_genre().get_name() + ", " + fromdb2.get_filetype().get_name() + ", " + str(fromdb2.get_checksum()))
    print("ID Film (original):  ")
    print(fromdb2)

    # ------ Test ob das gleiche Objekt aus dem Cache geholt wird ------

    fromdb2a = Film.get_by_id(film2.get_db_id())
    print("ID Film (aus Cache): ")
    print(fromdb2a)

    fromdb2b = Film.get_by_id(film2.get_db_id())
    print "ID Film (aus DB):    "
    print fromdb2b

    # Film 2 löschen und testen, ob es funktioniert hat
    print Film.get_cache().instances
    Film.delete(fromdb2)
    deleted = Film.get_by_id(film2.get_db_id())
    if deleted:
        print str(deleted.id) + deleted.get_titel() + ", " + deleted.get_pfad()
    else:
        print "Der Film mit der id %i wurde aus der Datenbank gelöscht!" % (film2.get_db_id())

def crawlerTest():
        # Datenbank leeren und neu erstellen für Test
        db = DbUtils()
        db.create_database()

        # Eigentlicher Test
        crawler = FilmCrawler()
        filme = crawler.crawl_folder("D:\Breaking Bad\Breakin_Bad_S05\Breakin_Bad-S05E01_-_Lebe_frei_oder_stirb.avi", True)
        print filme
        if filme:
            for film in filme:
                Film.persist(film)

        # Test ob ID von Film auch in DB landet
        test_db_film = Film.get_by_id(1)
        print test_db_film


if __name__ == '__main__':
    '''
    The main method of this python-script.
    Here the subprocedures are called with the initial directory where to start from 
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", action="store_true")

    # Achtung, hier muss ein sinnvolles Verzeichnis angegeben werden
    # crawlerTest()
    dbTests()

    args = parser.parse_args()
    if (args.d == True):
        dbTests()

    '''
    win = TTRFileChooser()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    fileOrFolder = Gtk.main()
    print fileOrFolder
    '''


