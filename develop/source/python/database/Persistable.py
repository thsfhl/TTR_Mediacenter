# -*- coding: utf-8 -*-

'''
Klasse f�r Entities, die in der DB gespeichert werden
'''


from .DbUtils import DbUtils

class Persistable(object):

    _db = None

    def __init__(self):
        """ Constructor """
        Persistable._db = DbUtils()

    @staticmethod
    def get_table_name():
        """ Gibt den Namen der Tabelle für diese Entity zurück. Benötigt für DB-Zugriff. """
        raise NotImplementedError

    @staticmethod
    def get_by_id(db_id):
        """ Gibt das Objekt mit der passenden ID aus der Datenbank zurück oder Null """
        raise NotImplementedError

    @staticmethod
    def get_all():
        """ Gibt das Objekt mit der passenden ID aus der Datenbank zurück oder Null """
        raise NotImplementedError

    def persist(self):
        """ Speichert das Objekt in die Datenbank """
        raise NotImplementedError

    def delete(self):
        """ Löscht das Objekt aus der Datenbank """
        if(self.get_db_id() and self.get_db_id() > 0):
            con = self.get_db().get_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM " + self.get_table_name() + " WHERE db_id = ?", (self.get_db_id(),))
            con.commit()
            cache = self.get_cache()
            if cache:
                cache.remove_from_cache(self)

    # -------------- Getter und Setter -------------------

    @staticmethod
    def get_db():
        if (Persistable._db == None):
            Persistable._db = DbUtils()
        return Persistable._db

    # set_db() gibt es nicht, da im Constructor gesetzt

    def get_db_id(self):
        return self._db_id

    def set_db_id(self, db_id):
        self._db_id = db_id



