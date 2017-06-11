# -*- coding: utf-8 -*-

import hashlib
from Persistable import Persistable
from Genre import Genre
from FileType import FileType
from ObjectCache import ObjectCache


class Film(Persistable):
    """
    Klasse in der die Datenbankverbindung hergestellt wird
    - Datenbank aktualisieren und erstellen
    - Wrapper für Abfragen
    """

    _cache = None

    def __init__(self, db_id=None, name=None, pfad=None, checksum=None, genre=None, filetype=None):
        """ Constructor """
        Persistable.__init__(self)
        self._name = name
        self._pfad = pfad
        self._checksum = checksum
        self._genre = genre
        self._filetype = filetype

    @staticmethod
    def get_cache():
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
        con = Film.get_db().get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, name, pfad, checksum, genre, filetype FROM " + Film.get_table_name() + " WHERE db_id=?", (db_id,))
        row = cur.fetchone()
        if row:
            film = Film.film_from_row(row)
            return film
        else:
            return None

    @staticmethod
    def get_all():
        """ Overridden aus Persistable """
        con = Film.get_db().get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, name, pfad, checksum, genre, filetype FROM " + Film.get_table_name())

        instances = []
        for row in cur:
            film = Film.film_from_row()
            instances.append(film)

        return instances

    @staticmethod
    def film_from_row(row):
        genre = Genre.get_cache().get_by_id(row[4])
        filetype = FileType.get_cache().get_by_id(row[4])
        film = Film(row[0], row[1], row[2], row[3], genre, filetype)
        return film

    def persist(self):
        """ Overridden aus Persistable """
        con = Film.get_db().get_connection()
        cur = con.cursor()

        genre_id = 0
        if self.get_genre():
            genre_id = self.get_genre().get_db_id()

        filetype_id = 0
        if self.get_filetype():
            filetype_id = self.get_filetype().get_db_id()

        if (self.get_db_id() > 0):
            cur.execute("UPDATE " + self.get_table_name() + " SET name=?, pfad=?, checksum=?, genre, filetype WHERE id=?",
                        (self.get_name(), self.get_pfad(), genre_id, filetype_id, self.get_db_id()))
        else:
            cur.execute("INSERT INTO " + self.get_table_name() + " (name, pfad, checksum, genre, filetype) VALUES (?,?,?,?,?)",
                        (self.get_name(), self.get_pfad(), self.get_checksum(), genre_id, filetype_id))
            self.set_db_id(cur.lastrowid)
        con.commit()

    # ------------ Für Crawler ------------

    @staticmethod
    def md5(fname):
        """
        Erzeugt eine MD5-Checksum für eine Datei
        Datei wird in Chunks von 4096 Bytes eingelesen, für den Fall,
        dass die Datei selbst zu groß ist, was bei Filmen ja durchaus möglich ist
        """
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
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
        cur.execute("SELECT db_id, name, pfad, checksum, genre, filetype FROM " + Film.get_table_name() + " WHERE pfad=?", (path,))
        row = cur.fetchone()
        if row:
            film = Film.film_from_row(row)
            return film
        else:
            return None


    # -------------- Getter und Setter -------------------

    # get/set db_id ist bereits in Persistable drin

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_pfad(self):
        return self._pfad

    def set_pfad(self, pfad):
        self._pfad = pfad
    
    def get_checksum(self):
        return self._checksum

    def set_checksum(self, checksum):
        self._checksum = checksum

    def get_genre(self):
        return self._genre

    def set_genre(self, genre):
        self._genre = genre

    def get_filetype(self):
        return self._filetype

    def set_filetype(self, filetype):
        self._filetype = filetype
