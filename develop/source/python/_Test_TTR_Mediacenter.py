# -*- coding: utf-8 -*-

# main file

import sys
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import argparse

mainPath = os.path.dirname(__file__)
sys.path.append(mainPath)

# DB-Klasse importieren
from database.DbUtils import DbUtils
from database.FileType import FileType
from database.Movie import Movie
from database.Genre import Genre
from MovieCrawler import FilmCrawler
from media.PlayerVLC import PlayerVLC
from layout.TTRFileChooser import TTRFileChooser
from Rtest import MainWindow

# nur zum Test
import hashlib

def addFilm(id, titel, pfad, filename, genre_id, filetype_id):
    # Film1 erzeugen und in DB speichern
    film = Movie()
    film.set_path(pfad)
    film.set_titel(titel)
    film.set_filename(filename)
    md5 = hashlib.md5()
    md5.update("Bam")
    film.set_checksum(md5.hexdigest())
    film.set_genre(Genre.get_by_id(genre_id))
    film.set_filetype(FileType.get_by_id(filetype_id))
    Movie.persist(film)
    return film

def dbTests(mainPath = None):
    # Reiner Testkram von Thomas - kann gerne wieder gelöscht werden
    # Test der Datenbank-Klasse
    db = DbUtils()

    # --------------------------------------------------------------------
    # Test von Thomas: Datenbank erzeugen und Abfrage ausgeben
    # --------------------------------------------------------------------

    # Löscht Datenbank und legt die Dabelle neu an
    db.create_database()

    # Test von Einträgen und dem Cache

    pfad = mainPath
    if (pfad == None):
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
    fromdb1 = Movie.get_by_id(film1.get_db_id())
    print(str(fromdb1.get_db_id()) + " - " + fromdb1.get_titel() + ", " + fromdb1.get_path() + ", " + fromdb1.get_genre().get_name() + ", " + fromdb1.get_filetype().get_name() + ", " + str(fromdb1.get_checksum()))

    fromdb2 = Movie.get_by_id(film2.get_db_id())
    print(str(fromdb2.get_db_id()) + " - " + fromdb2.get_titel() + ", " + fromdb2.get_path() + ", " + fromdb2.get_genre().get_name() + ", " + fromdb2.get_filetype().get_name() + ", " + str(fromdb2.get_checksum()))
    print("ID Film (original):  ")
    print(fromdb2)

    # ------ Test ob das gleiche Objekt aus dem Cache geholt wird ------

    fromdb2a = Movie.get_by_id(film2.get_db_id())
    print("ID Film (aus Cache): ")
    print(fromdb2a)

    fromdb2b = Movie.get_by_id(film2.get_db_id())
    print ("ID Film (aus DB):    ")
    print (fromdb2b)

    # Film 2 löschen und testen, ob es funktioniert hat
    print (Movie.get_cache().instances)
    Movie.delete(fromdb2)
    deleted = Movie.get_by_id(film2.get_db_id())
    if deleted:
        print (str(deleted.id) + deleted.get_titel() + ", " + deleted.get_path())
    else:
        print ("Der Film mit der id %i wurde aus der Datenbank gelöscht!" % (film2.get_db_id()))

def crawlerTest(folderOrFile = None):
        # Datenbank leeren und neu erstellen für Test
        db = DbUtils()
        db.create_database()

        # Eigentlicher Test
        crawler = FilmCrawler()
        if (folderOrFile == None):
            folderOrFile = os.path.join(os.getcwd(), "temp")
        # search in folder for movies etcpp and receive an array of those movies etc
        filme = crawler.crawl_folder(folderOrFile, True)
        # print (filme)
        if filme:
            # persist these movies
            for film in filme:
                Movie.persist(film)

        # Test ob ID von Film auch in DB landet
        test_db_film = Movie.get_by_id(1)
        # print (test_db_film)


if __name__ == '__main__':
    '''
    The main method of this python-script.
    Here the subprocedures are called with the initial directory where to start from 
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", action="store_true")

    # dbTests()

    args = parser.parse_args()
    if (args.d == True):
        dbTests(os.path.join(os.getcwd(), "temp"))


    # try the filechooser to get a file or a folder where to use the crawler
    win = TTRFileChooser()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()

    fileOrFolder = None
    # check if file/folder selection is canceled
    if ( not win.isCanceled() ):
        # file or folder which has been selected in filechooser windows
        fileOrFolder = win.getFileOrFolder()

    crawlerTest(fileOrFolder)

    # movies = Movie.get_all()
    # if (None != movies) and (len(movies) > 0):
    #     for m in movies:
    #         if (m.get_filetype().get_extension() != '.jpeg') and (m.get_filetype().get_extension() != '.jpg') and (m.get_filetype().get_extension() != '.png'):
    #             print ("Playing %s\n" % os.path.join(m.get_path(), m.get_filename()))
    #             player = PlayerVLC(os.path.join(m.get_path(),m.get_filename()))
    #             player.setup_objects_and_events()
    #             player.show()
    #             Gtk.main()
    #             player.player.stop()
    #             player.instance.release()
    # else:
    #     player = PlayerVLC(fileOrFolder)
    #     player.setup_objects_and_events()
    #     player.show()
    #     Gtk.main()
    #     player.player.stop()
    #     player.instance.release()
    #
    # global main
    main = MainWindow(mainPath) # create an instance of our class
    Gtk.main() # run the darn thing
