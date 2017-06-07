# -*- coding: utf-8 -*-

'''
Klasse in der die Datenbankverbindung hergestellt wird
- Datenbank aktualisieren und erstellen
- Wrapper für Abfragen
'''

import sqlite3 as sl
import sys
from Persistable import Persistable


class Film(Persistable):

    ''' Constructor '''
    def __init__(self, db_id=None, name=None, pfad=None):
        Persistable.__init__(self)
        self.db_id = db_id
        self.name = name
        self.pfad = pfad

    ''' Overridden aus Persistable '''
    @staticmethod
    def get_table_name():
        return "Filme"

    ''' Overridden aus Persistable '''
    @staticmethod
    def get_by_id(db_id):
        con = Film.db.get_connection()
        cur = con.cursor()
        cur.execute("SELECT db_id, name, pfad FROM " + Film.get_table_name() + " WHERE db_id=?", (db_id,))
        row = cur.fetchone()
        if row:
            film = Film(row[0], row[1], row[2])
            return film
        else:
            return None

    ''' Overridden aus Persistable '''
    def persist(self):
        con = Film.db.get_connection()
        cur = con.cursor()
        if(self.db_id > 0):
            cur.execute("UPDATE " + self.get_table_name() + " SET name=?, pfad=? WHERE id=?", (self.name, self.pfad, self.db_id))
        else:
            cur.execute("INSERT INTO " + self.get_table_name() + " (name, pfad) VALUES (?,?)", (self.name, self.pfad))
            self.db_id = cur.lastrowid
        con.commit()

