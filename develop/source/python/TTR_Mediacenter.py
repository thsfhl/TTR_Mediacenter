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

class TTR_Mediacenter(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)
        self.filetypes = []
        try:
            for f in FileType.get_all():
                self.filetypes = f[3]
        except Exception, e:
            self.filetypes.append(".gif")
            self.filetypes.append(".jpg")
            self.filetypes.append(".avi")
            self.filetypes.append(".png")
            self.filetypes.append(".jpeg")

        self.file = ""
        self.folder = ""


    def do_activate(self):
        win = TTRFileChooser(self.filetypes)
        win.connect("delete-event", Gtk.main_quit)
        win.show_all()
        Gtk.main()
        self.file = win.getFileName()
        self.folder = win.getFolderName()

    def getFileName(self):
        return self.file

    def getFolderName(self):
        return self.folder

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def addFilm(self, film, filmcache, pfad, id):
        # Film1 erzeugen und in DB speichern
        film = Film()
        film.set_pfad(pfad)
        film.set_name(film)
        checksum = hashlib.md5()
        checksum.update(pfad)
        film.set_checksum(checksum.hexdigest())
        film.set_genre(Genre.get_cache().get_by_id(id))
        film.set_filetype(FileType.get_cache().get_by_id(id))
        filmcache.persist(film)
        return film

    def dbTests(self):
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

        pfad = "c:\\erster_film.avi"
        film = "Dat is der erste Film"
        id = 1
        film1 = addFilm(film, filmcache, pfad, id)

        pfad = "c:\\zweiter_film.mpeg"
        film = "Dat ist der zweite Film"
        id = 2
        # Film2 erzeugen und in DB speichern
        film2 = addFilm(film, filmcache, pfad, id)

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


    def crawlerTest(self):
        # Datenbank leeren und neu erstellen für Test
        db = DbUtils()
        db.create_database()

        # Eigentlicher Test
        crawler = FilmCrawler()
        filme = crawler.crawl_folder("C:\\temp\\video_test", True)
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
    appl = TTR_Mediacenter()
    appl.do_activate()
#    exit_status = appl.run(sys.argv)

    name = appl.getFileName()
    if ("" == name):
        name = appl.getFolderName()

    print ("Folder/Filename = %s" % name)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", action="store_true")

    args = parser.parse_args()
    if (args.d == True):
        appl.dbTests()
        # Achtung, hier muss ein sinnvolles Verzeichnis angegeben werden
        appl.crawlerTest()
        # dbTests()


        # win = TTRFileChooser()
    # win.connect("delete-event", Gtk.main_quit)
    # win.show_all()
    # Gtk.main()


