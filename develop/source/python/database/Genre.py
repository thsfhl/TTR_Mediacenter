# -*- coding: utf-8 -*-

from .Persistable import Persistable
from .ObjectCache import ObjectCache


class Genre(Persistable):
    """
    Klasse in der die Datenbankverbindung hergestellt wird
    - Datenbank aktualisieren und erstellen
    - Wrapper für Abfragen
    """

    _cache = None

    def __init__(self, db_id=0, name=None):
        """ Constructor """
        Persistable.__init__(self)
        self._db_id = db_id
        self._name = name

    @staticmethod
    def get_cache():
        """
        Liefert entweder das Cache-Objekt oder legt den Cache an, falls nicht vorhanden
        :return: ObjectCache zu Genre
        """
        if not Genre._cache:
            Genre._cache = ObjectCache(Genre().__class__)
        return Genre._cache

    @staticmethod
    def get_table_name():
        """ Overridden aus Persistable """
        return "Genres"

    @staticmethod
    def get_by_id(db_id):
        """ Overridden aus Persistable """
        # Try to get from Cache
        genre = Genre.get_cache().get_by_id(db_id)
        if genre:
            return genre

        con = Genre.get_db().get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, name FROM " + Genre.get_table_name() + " WHERE db_id=?", (db_id,))
        row = cur.fetchone()
        if row:
            genre = Genre(row[0], row[1])
            Genre.get_cache().add_to_cache(genre)
            return genre
        else:
            return None

    @staticmethod
    def get_all():
        """ Overridden aus Persistable """
        con = Genre.get_db().get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, name FROM " + Genre.get_table_name())

        instances = []
        for row in cur:
            genre = Genre(row[0], row[1])
            instances.append(genre)
            Genre.get_cache().add_to_cache(genre)

        return instances

    def persist(self):
        """ Overridden aus Persistable """
        con = Genre.get_db().get_connection()
        cur = con.cursor()
        if self.get_db_id() > 0:
            cur.execute("UPDATE " + self.get_table_name() + " SET name=? WHERE id=?",
                        (self.get_name(), self.get_db_id()))
        else:
            cur.execute("INSERT INTO " + self.get_table_name() + " (name) VALUES (?)",
                        (self.get_name()))
            self.set_db_id(cur.lastrowid)
        con.commit()
        Genre.get_cache().add_to_cache(self)

    # -------------- Getter und Setter -------------------

    # get/set db_id ist bereits in Persistable drin

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name
