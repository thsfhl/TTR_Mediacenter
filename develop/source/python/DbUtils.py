# -*- coding: utf-8 -*-

'''
Klasse in der die Datenbankverbindung hergestellt wird
- Datenbank aktualisieren und erstellen
- Wrapper für Abfragen
'''

import sqlite3 as sl
import sys
from Singleton import *


@singleton
class DbUtils:

    ''' Constructor '''
    def __init__(self):
        # Datenbank-Attribut mit None initialisieren
        self.con = None

    ''' Destructor - Beendet Datenbankverbindung beim Löschen '''
    def __del__(self):
        # Datenbankverbindung beenden, falls eine besteht
        if self.con:
            self.con.close()
    '''
    Singleton für die Datenbankverbindung
    Gibt die aktuelle Verbindung zurück oder erzeugt eine, falls diese nicht existiert
    '''
    def get_connection(self):
        try:
            if not self.con:
                # Falls noch keine Datenbankverbindung besteht, diese herstellen
                self.con = sl.connect('ttr_mediacenter.db')

            return self.con

        except sl.Error, e:

            # Fehlermeldung, falls Verbindung nicht hergestellt werden konnte
            print "Error %s:" % e.args[0]
            sys.exit(1)

    def get_cursor(self):
        return self.get_connection().cursor()

    def create_database(self):
        cur = self.get_cursor()

        # Tables erzeugen, ggf. vorher löschen
        cur.execute("DROP TABLE IF EXISTS Filme")
        cur.execute("CREATE TABLE Filme("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "name Text, "
                    "pfad Text "            
                    ")"
                    )


