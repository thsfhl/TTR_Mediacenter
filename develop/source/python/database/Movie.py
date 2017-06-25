# -*- coding: utf-8 -*-

import hashlib
import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

from .Persistable import Persistable
from .Genre import Genre
from .FileType import FileType
from .ObjectCache import ObjectCache

class Movie(Persistable, GObject.GObject):
    """
    Klasse in der die Datenbankverbindung hergestellt wird
    - Datenbank aktualisieren und erstellen
    - Wrapper fuer Abfragen
    """

    # Konstanten f�r den Dateistatus
    STATUS_OK = 0
    STATUS_CHANGED = 1
    STATUS_DELETED = 2

    _cache = None

    def __init__(self, db_id=0, title=None, path=None, filename=None, checksum=None, genre_list=None, filetype=None, image=None, status=0):
        """ Constructor """
        Persistable.__init__(self)
        GObject.GObject.__init__(self)
        self._db_id = db_id
        self._title = title
        self._path = path
        self._filename = filename
        self._checksum = checksum
        if genre_list:
            self._genre_list = genre_list
        else:
            self._genre_list = []
        self._filetype = filetype
        self._status = status # Status 0 = OK, 1 = Changed, 2 = Deleted
        self._image = image

    @staticmethod
    def get_cache():
        """
        Liefert entweder das Cache-Objekt oder legt den Cache an, falls nicht vorhanden
        :return: ObjectCache zu Movie
        """
        if not Movie._cache:
            Movie._cache = ObjectCache(Movie().__class__)
        return Movie._cache

    @staticmethod
    def get_table_name():
        """ Overridden aus Persistable """
        return "Movies"

    @staticmethod
    def get_by_id(db_id):
        """ Overridden aus Persistable """
        # Im Cache nachschauen, ob es eine Instanz gibt
        movie = Movie.get_cache().get_by_id(db_id)
        if movie:
            return movie

        # Falls nicht aus Datenbank holen
        con = Movie.get_db().get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, title, path, filename, checksum, filetype, image FROM " + Movie.get_table_name() + " WHERE db_id=?", (db_id,))
        row = cur.fetchone()
        if row:
            movie = Movie.movie_from_row(row)

            Movie.get_cache().add_to_cache(movie)
            return movie
        else:
            return None

    def fetch_genres_from_db(self):
        """
        Holt zu einem Movie die Liste der Genres aus der Datenbank und f�gt sie dem Objekt hinzu
        :return: 
        """
        con = Movie.get_db().get_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT genre_id FROM MovieGenre WHERE movie_id=?", (self.get_db_id(),))

        for row in cur:
            genre = Genre.get_by_id(row[0])
            self.add_genre(genre)

    @staticmethod
    def get_all():
        """ Overridden aus Persistable """
        con = Movie.get_db().get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, title, path, filename, checksum, filetype, image FROM " + Movie.get_table_name())

        instances = []
        for row in cur:
            movie = Movie.movie_from_row(row)
            instances.append(movie)
            Movie.get_cache().add_to_cache(movie)

        return instances

    @staticmethod
    def movie_from_row(row):
        """
        Erzeugt ein Movie-Objekt aus einer Datenbankzeile
        
        :param row: Passende Datenbankzeile 
        :return: Movie-Objekt
        """
        filetype = FileType.get_by_id(row[5])
        movie = Movie(row[0], row[1], row[2], row[3], row[4], None, filetype, row[6])
        movie.fetch_genres_from_db()
        movie.determine_status()
        return movie

    def persist(self):
        """ Overridden aus Persistable """
        con = Movie.get_db().get_connection()
        cur = con.cursor()

        filetype_id = 0
        if self.get_filetype():
            filetype_id = self.get_filetype().get_db_id()


        if (not self.get_db_id() is None and  self.get_db_id()):
            cur.execute("UPDATE " + self.get_table_name() + " SET title=?, path=?, filename=?, checksum=?, filetype=?, image=? WHERE db_id=?",
                        (self.get_title(), self.get_path(), self.get_filename(), self.get_checksum(), filetype_id, self.get_image(), self.get_db_id()))
        else:
            cur.execute("INSERT INTO " + self.get_table_name() + " (title, path, filename, checksum, filetype, image) VALUES (?, ?, ?, ?, ?, ?)",
                        (self.get_title(), self.get_path(), self.get_filename(), self.get_checksum(), filetype_id, self.get_image()))
            self.set_db_id(cur.lastrowid)
        con.commit()

        # ToDo: Genre-Assoziationen löschen, die genre_list nicht hergibt
        genre_ids = []
        for genre in self.get_genre_list():
            genre_ids.append(genre.get_db_id())

        if genre_ids:
            placeholders = ', '.join('?' * len(genre_ids))

            query = "DELETE FROM MovieGenre WHERE movie_id = ? AND genre_id NOT IN (%s)" % placeholders
            parameters = [self.get_db_id()] + genre_ids
            cur.execute(query, parameters)
            con.commit()

        # ToDo: Genre-Assoziationen erzeugen, die genre_list zusätzlich enthält
        query = "INSERT OR IGNORE INTO MovieGenre(movie_id, genre_id) VALUES (?, ?)"
        for genre in self.get_genre_list():
            cur.execute(query, (self.get_db_id(), genre.get_db_id()))
        con.commit()

        # Cache aktualsieren
        Movie.get_cache().add_to_cache(self)

    @staticmethod
    def md5(fname):
        """
        Erzeugt eine MD5-Checksum f�r max. die ersten 8MB einer Datei.
        Datei wird in Chunks von 4096 Bytes eingelesen, für den Fall,
        dass die Datei selbst zu groß ist, was bei Movieen ja durchaus möglich ist
        """
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            blocks_read = 0
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
                blocks_read += 1
                # Nur erste 2000 Bl�cke lesen 4086 Bytes * 2000 = 8 MB
                if blocks_read >= 100:
                    break
        return hash_md5.hexdigest()

    def determine_status(self):
        """
        Prueft ob der Pfad noch existiert und vergleicht die gespeicherte Checksum
        des Movie mit Datei auf die der Pfad zeigt. Entsprechend wird der Status
        des Movies gesetzt und als Wert zurueckgegeben.
        """
        if(os.path.isfile(self.get_full_path())):
            checksum = Movie.md5(self.get_full_path())
            if(self.get_checksum() == checksum):
                self.set_status(Movie.STATUS_OK)

            else:
                self.set_status(Movie.STATUS_CHANGED)
        else:
            self.set_status(Movie.STATUS_DELETED)

        # Neuen Status zurueckgeben
        return self.get_status

    @staticmethod
    def get_by_path(path):
        """
        Sucht einen Movie anhand des Pfads. Wird keiner gefunden wird None zurückgegeben, sonst der Movie
        """
        con = Movie.get_db().get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, title, path, filename, checksum, filetype, image FROM " + Movie.get_table_name() + " WHERE path=?", (path,))
        row = cur.fetchone()
        if row:
            movie = Movie.get_cache().get_by_id(row[0])
            if not movie:
                movie = Movie.movie_from_row(row)
                Movie.get_cache().add_to_cache(movie)
            return movie
        else:
            return None

    @staticmethod
    def read_file_to_movie(path):
        """
        Nimmt eine Datei entgegen und liefert, falls es sich um einen Movie handelt,
        ein Movie-Objekt zurück. Anderenfalls None

        :param path: Pfad zur Datei 
        :return: Movie oder None
        """
        # Dateiendung prüfen und dabei FileType ermitteln
        path_folder, filename = os.path.split(path)
        file_root, file_extension = os.path.splitext(filename)
        filetype = FileType.get_by_extension(file_extension.lower())

        if not filetype:
            return None

        # Eigenschaften auslesen
        # Genre = Null, falls nicht in Metadaten vorhanden
        movie_from_db = Movie.get_by_path(path)
        if movie_from_db:
            # Ein Movie mit diesem Pfad existiert bereits in der DB
            if movie_from_db.checksum_changed():
                # Checksum neu setzen
                movie_from_db.set_checksum(movie_from_db.md5(path))
                movie_from_db.set_status(
                    1)  # Status auf "geänderte Datei" setzen / ggf. später auch Metadaten neu lesen
                Movie.persist(movie_from_db)
            return movie_from_db

        # Falls der Movie noch nicht in der Datenbank war
        movie_neu = Movie(0, file_root, path_folder, filename, Movie.md5(path), None, filetype)

        return movie_neu

    def update_values(self, movie):
        """
        Aktualisiert bestehendes Movie mit den Properties eines existierenden Movies
        :param movie:
        :return:
        """
        self.set_title(movie.get_title())
        self.set_path(movie.get_path())
        self.set_filename(movie.get_filename())
        self.set_checksum(movie.get_checksum())
        self._genre_list = movie.get_genre_list()
        self.set_filetype(movie.get_filetype())
        self.set_status(movie.get_status())
        self.set_image(movie.get_image())
    
    def get_copy(self):
        """
        Erzeugt eine Kopie eines bestehenden Movies. Ist nur gedacht, um Änderungen an einer Kopie
        vorzunehmen, die später per updateFromCopy() wieder in ein "echtes" Movie zurückgeführt werden.
        """
        copy = Movie(self.get_db())
        copy.update_values(self)
        return copy
        
        
    # -------------- Getter und Setter -------------------

    # get/set db_id ist bereits in Persistable drin

    def get_title(self):
        return self._title

    def set_title(self, title):
        self._title = title

    def get_path(self):
        return self._path

    def set_path(self, path):
        self._path = path

    def get_filename(self):
        return self._filename

    def set_filename(self, filename):
        self._filename = filename

    #Zusammengesetzt aus path und filename
    def get_full_path(self):
        return os.path.join(self.get_path(), self.get_filename())
    
    def get_checksum(self):
        return self._checksum

    def set_checksum(self, checksum):
        self._checksum = checksum

    def get_genre_list(self):
        return self._genre_list

    def add_genre(self, genre):
        if genre not in self._genre_list:
            self._genre_list.append(genre)

    def remove_genre(self, genre):
        self._genre_list.remove(genre)

    def clear_genre_list(self):
        self._genre_list = []

    def get_filetype(self):
        return self._filetype

    def set_filetype(self, filetype):
        self._filetype = filetype

    def get_image(self):
        return self._image

    def set_image(self, image):
        self._image = image
        
    def get_status(self):
        return self._status

    def set_status(self, status):
        self._status = status
