# -*- coding: utf-8 -*-

from Persistable import Persistable
from ObjectCache import ObjectCache


class FileType(Persistable):
    """
    Klasse in der die Datenbankverbindung hergestellt wird
    - Datenbank aktualisieren und erstellen
    - Wrapper für Abfragen
    """

    _cache = None

    def __init__(self, db_id=None, name=None, extension=None):
        """ Constructor """
        Persistable.__init__(self)
        self.set_db_id(db_id)
        self._name = name
        self._extension = None
        self.set_extension(extension)

    @staticmethod
    def get_cache():
        if not FileType._cache:
            FileType._cache = ObjectCache(FileType().__class__)
        return FileType._cache

    @staticmethod
    def get_table_name():
        """ Overridden aus Persistable """
        return "FileTypes"

    @staticmethod
    def get_by_id(db_id):
        """ Overridden aus Persistable """
        con = FileType.get_db().get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, name, extension FROM " + FileType.get_table_name() + " WHERE db_id=?", (db_id,))
        row = cur.fetchone()
        if row:
            film = FileType(row[0], row[1], row[2])
            return film
        else:
            return None

    @staticmethod
    def get_all():
        """ Overridden aus Persistable """
        con = FileType.get_db().get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, name, extension FROM " + FileType.get_table_name())

        instances = []
        for row in cur:
            film = FileType(row[0], row[1], row[2])
            instances.append(film)

        return instances

    def persist(self):
        """ Overridden aus Persistable """
        con = FileType.get_db().get_connection()
        cur = con.cursor()
        if self.get_db_id() > 0:
            cur.execute("UPDATE " + self.get_table_name() + " SET name=?, extension=? WHERE id=?",
                        (self.get_name(), self.get_extension(), self.get_db_id()))
        else:
            cur.execute("INSERT INTO " + self.get_table_name() + " (name, extension) VALUES (?, ?)",
                        (self.get_name(), self.get_extension()))
            self.set_db_id(cur.lastrowid)
        con.commit()

    # -------------- Getter und Setter -------------------

    # get/set db_id ist bereits in Persistable drin

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name
        
    def get_extension(self):
        return self._extension

    def set_extension(self, extension):
        if extension:
            self._extension = extension.lower()
        else:
            self._extension = None

