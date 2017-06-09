# -*- coding: utf-8 -*-

from Persistable import Persistable
from ObjectCache import ObjectCache


class Genre(Persistable):
    """
    Klasse in der die Datenbankverbindung hergestellt wird
    - Datenbank aktualisieren und erstellen
    - Wrapper für Abfragen
    """

    _cache = None

    def __init__(self, db_id=None, name=None):
        """ Constructor """
        Persistable.__init__(self)
        self.db_id = db_id
        self.name = name

    @staticmethod
    def get_cache():
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
        con = Genre.db.get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, name FROM " + Genre.get_table_name() + " WHERE db_id=?", (db_id,))
        row = cur.fetchone()
        if row:
            film = Genre(row[0], row[1])
            return film
        else:
            return None

    @staticmethod
    def get_all():
        """ Overridden aus Persistable """
        con = Genre.db.get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, name FROM " + Genre.get_table_name())

        instances = []
        for row in cur:
            film = Genre(row[0], row[1])
            instances.append(film)

        return instances

    def persist(self):
        """ Overridden aus Persistable """
        con = Genre.db.get_connection()
        cur = con.cursor()
        if (self.db_id > 0):
            cur.execute("UPDATE " + self.get_table_name() + " SET name=? WHERE id=?",
                        (self.name, self.db_id))
        else:
            cur.execute("INSERT INTO " + self.get_table_name() + " (name) VALUES (?)",
                        (self.name))
            self.db_id = cur.lastrowid
        con.commit()