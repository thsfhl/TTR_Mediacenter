# -*- coding: utf-8 -*-

import hashlib
import os
from gi.repository import GObject

from .Persistable import Persistable
from .Genre import Genre
from .FileType import FileType
from .ObjectCache import ObjectCache

class Film(Persistable, GObject.GObject):
    """
    Klasse in der die Datenbankverbindung hergestellt wird
    - Datenbank aktualisieren und erstellen
    - Wrapper für Abfragen
    """

    _cache = None
    def __init__(self, db_id=None, titel=None, pfad=None, filename=None, checksum=None, genre_list=None, filetype=None, status=0):
        """ Constructor """
        Persistable.__init__(self)
        GObject.GObject.__init__(self)
        self._db_id = db_id
        self._titel = titel
        self._pfad = pfad
        self._filename = filename
        self._checksum = checksum
        if genre_list:
            self._genre_list = genre_list
        else:
            self._genre_list = []
        self._filetype = filetype
        self._status = status # Status 0 = OK, 1 = Changed, 2 = Deleted
        self._image = None

    @staticmethod
    def get_cache():
        """
        Liefert entweder das Cache-Objekt oder legt den Cache an, falls nicht vorhanden
        :return: ObjectCache zu Film
        """
        if not Film._cache:
            Film._cache = ObjectCache(Film().__class__)
        return Film._cache

    @staticmethod
    def get_table_name():
        """ Overridden aus Persistable """
        return "Filme"

    @staticmethod
    def get_by_id(db_id):
        """ Overridden aus Persistable """
        # Im Cache nachschauen, ob es eine Instanz gibt
        film = Film.get_cache().get_by_id(db_id)
        if film:
            return film

        # Falls nicht aus Datenbank holen
        con = Film.get_db().get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, titel, pfad, filename, checksum, filetype, image FROM " + Film.get_table_name() + " WHERE db_id=?", (db_id,))
        row = cur.fetchone()
        if row:
            film = Film.film_from_row(row)

            Film.get_cache().add_to_cache(film)
            return film
        else:
            return None

    def fetch_genres_from_db(self):
        """
        Holt zu einem Film die Liste der Genres aus der Datenbank und fügt sie dem Objekt hinzu
        :return: 
        """
        con = Film.get_db().get_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT genre_id FROM FilmGenre WHERE film_id=?", (self.get_db_id(),))

        for row in cur:
            genre = Genre.get_by_id(row[0])
            self.add_genre(genre)

    @staticmethod
    def get_all():
        """ Overridden aus Persistable """
        con = Film.get_db().get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, titel, pfad, filename, checksum, filetype, image FROM " + Film.get_table_name())

        instances = []
        for row in cur:
            film = Film.film_from_row(row)
            instances.append(film)
            Film.get_cache().add_to_cache(film)

        return instances

    @staticmethod
    def film_from_row(row):
        """
        Erzeugt ein Film-Objekt aus einer Datenbankzeile
        
        :param row: Passende Datenbankzeile 
        :return: Film-Objekt
        """
        filetype = FileType.get_by_id(row[5])
        film = Film(row[0], row[1], row[2], row[3], row[4], None, filetype, row[6])
        film.fetch_genres_from_db()
        return film

    def persist(self):
        """ Overridden aus Persistable """
        con = Film.get_db().get_connection()
        cur = con.cursor()

        filetype_id = 0
        if self.get_filetype():
            filetype_id = self.get_filetype().get_db_id()

        if (self.get_db_id() > 0):
            cur.execute("UPDATE " + self.get_table_name() + " SET titel=?, pfad=?, filename=?, checksum=?, filetype=?, image=? WHERE id=?",
                        (self.get_titel(), self.get_pfad(), self.get_filename(), self.get_checksum(), filetype_id, self.get_image(), self.get_db_id()))
        else:
            cur.execute("INSERT INTO " + self.get_table_name() + " (titel, pfad, filename, checksum, filetype, image) VALUES (?, ?, ?, ?, ?, ?)",
                        (self.get_titel(), self.get_pfad(), self.get_filename(), self.get_checksum(), filetype_id, self.get_image()))
            self.set_db_id(cur.lastrowid)
        con.commit()

        # ToDo: Genre-Assoziationen löschen, die genre_list nicht hergibt
        genre_ids = []
        for genre in self.get_genres():
            genre_ids.append(genre.get_db_id())

        if genre_ids:
            placeholders = ', '.join('?' * len(genre_ids))

            query = "DELETE FROM FilmGenre WHERE film_id = ? AND genre_id NOT IN (%s)" % placeholders
            parameters = [self.get_db_id()] + genre_ids
            cur.execute(query, parameters)
            con.commit()

        # ToDo: Genre-Assoziationen erzeugen, die genre_list zusätzlich enthält
        query = "INSERT INTO FilmGenre(film_id, genre_id) VALUES (?, ?)"
        for genre in self.get_genres():
            cur.execute(query, (self.get_db_id(), genre.get_db_id()))
        con.commit()

        # Cache aktualsieren
        Film.get_cache().add_to_cache(self)

    # ------------ Für Crawler ------------

    @staticmethod
    def md5(fname):
        """
        Erzeugt eine MD5-Checksum für max. die ersten 8MB einer Datei.
        Datei wird in Chunks von 4096 Bytes eingelesen, für den Fall,
        dass die Datei selbst zu groß ist, was bei Filmen ja durchaus möglich ist
        """
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            blocks_read = 0
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
                blocks_read += 1
                # Nur erste 2000 Blöcke lesen 4086 Bytes * 2000 = 8 MB
                if blocks_read >= 100:
                    break
        return hash_md5.hexdigest()

    def checksum_changed(self):
        """
        Vergleicht die gespeicherte Checksum des Films mit Datei auf die der Pfad zeigt
        """
        checksum = Film.md5(self.get_pfad())
        return self.get_checksum() == checksum

    @staticmethod
    def get_by_path(path):
        """
        Sucht einen Film anhand des Pfads. Wird keiner gefunden wird None zurückgegeben, sonst der Film
        """
        con = Film.get_db().get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, titel, pfad, filename, checksum, filetype, image FROM " + Film.get_table_name() + " WHERE pfad=?", (path,))
        row = cur.fetchone()
        if row:
            film = Film.get_cache().get_by_id(row[0])
            if not film:
                film = Film.film_from_row(row)
                Film.get_cache().add_to_cache(film)
            return film
        else:
            return None

    @staticmethod
    def read_file_to_film(path):
        """
        Nimmt eine Datei entgegen und liefert, falls es sich um einen Film handelt,
        ein Film-Objekt zurück. Anderenfalls None

        :param path: Pfad zur Datei 
        :return: Film oder None
        """
        # Dateiendung prüfen und dabei FileType ermitteln
        path_folder, filename = os.path.split(path)
        file_root, file_extension = os.path.splitext(filename)
        filetype = FileType.get_by_extension(file_extension.lower())

        if not filetype:
            return None

        # Eigenschaften auslesen
        # Genre = Null, falls nicht in Metadaten vorhanden
        film_aus_db = Film.get_by_path(path)
        if film_aus_db:
            # Ein Film mit diesem Pfad existiert bereits in der DB
            if film_aus_db.checksum_changed():
                # Checksum neu setzen
                film_aus_db.set_checksum(film_aus_db.md5(path))
                film_aus_db.set_status(
                    1)  # Status auf "geänderte Datei" setzen / ggf. später auch Metadaten neu lesen
                Film.persist(film_aus_db)
            return film_aus_db

        # Falls der Film noch nicht in der Datenbank war
        film_neu = Film(None, file_root, path_folder, filename, Film.md5(path), None, filetype)

        return film_neu

    # -------------- Getter und Setter -------------------

    # get/set db_id ist bereits in Persistable drin

    def get_titel(self):
        return self._titel

    def set_titel(self, titel):
        self._titel = titel

    def get_pfad(self):
        return self._pfad

    def set_pfad(self, pfad):
        self._pfad = pfad

    def get_filename(self):
        return self._filename

    def set_filename(self, filename):
        self._filename = filename
    
    def get_checksum(self):
        return self._checksum

    def set_checksum(self, checksum):
        self._checksum = checksum

    def get_genres(self):
        return self._genre_list

    def add_genre(self, genre):
        if genre not in self._genre_list:
            self._genre_list.append(genre)

    def remove_genre(self, genre):
        self._genre_list.remove(genre)

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
