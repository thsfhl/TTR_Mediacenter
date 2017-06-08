# -*- coding: utf-8 -*-

# ToDo: MD5-Hash muss immer berechnet werden, wenn "pfad" neu gesetzt wird

import sqlite3 as sl
import sys
import hashlib
from Persistable import Persistable
from ObjectCache import ObjectCache


class Film(Persistable):
    """
    Klasse in der die Datenbankverbindung hergestellt wird
    - Datenbank aktualisieren und erstellen
    - Wrapper für Abfragen
    """

    cache = None

    def __new__(cls, *args, **kwargs):
        if not Film.cache:
            Film.cache = ObjectCache(cls)
        return super(Film, cls).__new__(cls)

    def __init__(self, db_id=None, name=None, pfad=None, checksum=None):
        """ Constructor """
        Persistable.__init__(self)
        self.db_id = db_id
        self.name = name
        self.pfad = pfad
        self.checksum = checksum

    @staticmethod
    def get_table_name():
        """ Overridden aus Persistable """
        return "Filme"

    @staticmethod
    def get_by_id(db_id):
        """ Overridden aus Persistable """
        con = Film.db.get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, name, pfad, checksum FROM " + Film.get_table_name() + " WHERE db_id=?", (db_id,))
        row = cur.fetchone()
        if row:
            film = Film(row[0], row[1], row[2], row[3])
            return film
        else:
            return None

    def persist(self):
        """ Overridden aus Persistable """
        con = Film.db.get_connection()
        cur = con.cursor()
        if (self.db_id > 0):
            cur.execute("UPDATE " + self.get_table_name() + " SET name=?, pfad=?, checksum=? WHERE id=?",
                        (self.name, self.pfad, self.db_id))
        else:
            cur.execute("INSERT INTO " + self.get_table_name() + " (name, pfad, checksum) VALUES (?,?,?)",
                        (self.name, self.pfad, self.checksum))
            self.db_id = cur.lastrowid
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
        checksum = Film.md5(self.pfad)
        return self.checksum == checksum

    @staticmethod
    def get_by_path(path):
        """
        Sucht einen Film anhand des Pfads. Wird keiner gefunden wird None zurückgegeben, sonst der Film
        """
        con = Film.db.get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, name, pfad, checksum FROM " + Film.get_table_name() + " WHERE pfad=?", (path,))
        row = cur.fetchone()
        if row:
            film = Film(row[0], row[1], row[2], row[3])
            return film
        else:
            return None
