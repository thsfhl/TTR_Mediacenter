# -*- coding: utf-8 -*-

'''
Klasse für Entities, die in der DB gespeichert werden
'''

import abc
from DbUtils import DbUtils

class Persistable:
    __metaclass__ = abc.ABCMeta

    db = None

    def __init__(self, db_id=None):
        Persistable.db_id = db_id
        Persistable.db = DbUtils()

    @staticmethod
    @abc.abstractmethod
    def get_table_name():
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def get_by_id(db_id):
        # Objekt anhand von ID aus DB laden
        raise NotImplementedError

    @abc.abstractmethod
    def persist(self):
        # Speichern des Objekts (INSERT OR UPDATE)
        raise NotImplementedError

    def delete(self):
        # Löschen des Objekts aus der Datenbank
        if(self.db_id and self.db_id > 0):
            con = self.db.get_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM " + self.get_table_name() + " WHERE db_id = ?", (self.db_id,))
            con.commit()


