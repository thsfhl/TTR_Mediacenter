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
        """ Constructor """
        Persistable.db_id = db_id
        Persistable.db = DbUtils()

    @staticmethod
    @abc.abstractmethod
    def get_table_name():
        """ Gibt den Namen der Tabelle für diese Entity zurück. Benötigt für DB-Zugriff. """
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def get_by_id(db_id):
        """ Gibt das Objekt mit der passenden ID aus der Datenbank zurück oder Null """
        raise NotImplementedError

    @abc.abstractmethod
    def persist(self):
        """ Speichert das Objekt in die Datenbank """
        raise NotImplementedError

    def delete(self):
        """ Löscht das Objekt aus der Datenbank """
        if(self.db_id and self.db_id > 0):
            con = self.db.get_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM " + self.get_table_name() + " WHERE db_id = ?", (self.db_id,))
            con.commit()


