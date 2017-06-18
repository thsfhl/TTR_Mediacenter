# -*- coding: utf-8 -*-

import sqlite3 as sl
import sys
from database.Singleton import Singleton


@Singleton
class DbUtils:
    """
    Klasse in der die Datenbankverbindung hergestellt wird
    - Datenbank aktualisieren und erstellen
    - Wrapper für Abfragen
    """

    def __init__(self):
        """ Constructor """
        # Datenbank-Attribut mit None initialisieren
        self.con = None

    def __del__(self):
        """ Destructor - Beendet Datenbankverbindung beim Löschen """
        # Datenbankverbindung beenden, falls eine besteht
        if self.con:
            self.con.close()

    def get_connection(self):
        """
        Singleton für die Datenbankverbindung
        Gibt die aktuelle Verbindung zurück oder erzeugt eine, falls diese nicht existiert
        """
        try:
            if not self.con:
                # Falls noch keine Datenbankverbindung besteht, diese herstellen
                self.con = sl.connect('ttr_mediacenter.db')

            return self.con

        except sl.Error as e:
            # Fehlermeldung, falls Verbindung nicht hergestellt werden konnte
            print("Error %s:" % e.args[0])
            sys.exit(1)

    def create_database(self):
        """ Löscht und erstellt die Datenbank """
        con = self.get_connection()
        cur = con.cursor()

        # Tabellen erzeugen, ggf. vorher löschen
        self.createTableFilme(cur)
        self.createTableGenres(cur)
        self.createTableFileTypes(cur)
        self.createTableFilmGenre(cur)

        # Statements auf DB ausführen
        con.commit()

    # Tabelle FileTypes anlegen und mit Standardwerten füllen
    def createTableFileTypes(self, cur):
        # Table für die FileTypes
        cur.execute("DROP TABLE IF EXISTS FileTypes")
        cur.execute("CREATE TABLE FileTypes("
                    "db_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "name Text NOT NULL,"
                    "extension Text NOT NULL UNIQUE"
                    ")"
                    )
        # Default-Werte setzen
        filetypes = [('AVI', '.avi'),
                     ('MPEG', '.mpeg'),
                     ('MPEG', '.mpg'),
                     ('Windows Media Video', '.wmv'),
                     ('Flash Video', '.flv'),
                     ('QuickTime File Format', '.mov'),
                     ('Containerformat / MOTION PICTURE EXPERTS GROUP 4,' , '.mp4'),
                     ('Joint Photographic Experts Group', '.jpeg'),
                     ('Joint Photographic Experts Group', '.jpg'),
                     ('Portable Network Graphics', '.png')
                     ]
        cur.executemany("INSERT INTO FileTypes(name, extension) VALUES(?, ?)", filetypes)

    # Tabelle Genres anlegen und mit Standardwerten füllen
    def createTableGenres(self, cur):
        # Table für die Genres
        cur.execute("DROP TABLE IF EXISTS Genres")
        cur.execute("CREATE TABLE Genres("
                    "db_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "name Text NOT NULL UNIQUE "
                    ")"
                    )
        # Default-Werte setzen
        genres = [('Horror',),
                  ('Komoedie',),
                  ('Science Fiction',),
                  ('Dokumentation',),
                  ('Action',)
                  ]
        cur.executemany("INSERT INTO Genres(name) VALUES(?)", genres)

    # Tabelle Filme anlegen
    def createTableFilme(self, cur):
        # Table für die Filme
        cur.execute("DROP TABLE IF EXISTS Filme")
        cur.execute("CREATE TABLE Filme("
                    "db_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "titel Text NOT NULL, "
                    "pfad Text NOT NULL, "
                    "filename Text NOT NULL, "
                    "checksum Text NOT NULL, "
                    "filetype INTEGER, "
                    "image Text, "
                    "UNIQUE (pfad, filename), "
                    "FOREIGN KEY(filetype) REFERENCES FileTypes(db_id)"        
                    ")"
                    )
        # Index zum Suchen, wenn eine neue Datei hinzugefügt wird
        cur.execute("CREATE INDEX index_pfad ON Filme(pfad, filename)")

    # Tabelle Filme anlegen
    def createTableFilmGenre(self, cur):
        # Table für die Filme
        cur.execute("DROP TABLE IF EXISTS FilmGenre")
        cur.execute("CREATE TABLE FilmGenre("
                    "film_id INTEGER NOT NULL, "
                    "genre_id INTEGER NOT NULL, "
                    "UNIQUE (film_id, genre_id), "
                    "FOREIGN KEY(film_id) REFERENCES Film(db_id) ON DELETE CASCADE, "
                    "FOREIGN KEY(genre_id) REFERENCES Genre(db_id) ON DELETE CASCADE"
                    ")"
                    )
        # Index zum Suchen, wenn eine neue Datei hinzugefügt wird
        cur.execute("CREATE INDEX index_film_genre ON FilmGenre(film_id, genre_id)")

