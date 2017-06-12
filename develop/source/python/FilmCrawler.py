# -*- coding: utf-8 -*-

from database.Film import Film
from database.FileType import FileType
import os


class FilmCrawler:
    def __init__(self):
        pass

    def crawl_folder(self, base_path, crawl_subfolders=False, rel_path=""):
        """
        Sucht Dateien innerhalb des übergebenen Pfades aus und ruft sich selbst
        für jeden Eintrag auf, der wiederum ein Ordner ist, falls crawl_subfolder == true

        Je passt die Dateiendung zu einer der Endungen in "FileType", wird die Datei
        ausgelesen, in ein Film-Objekt umgewandelt und dann im Array zurückgegeben.

        :param base_path: Basispfad, der beim ersten Aufruf angegeben wird
        :param rel_path: Relativer Pfad des Elements zum Basispfad
        :param crawl_subfolders: Flag, ob Unterordner durchsucht werden sollen
        :return: Kein Rückgabewert, sondern Ausgabe auf der Konsole
        """

        filme = []

        # Dateinamen in Unicode umwandeln, damit diese später sauber in SQLite geschrieben werden können
        base_path = unicode(base_path)
        rel_path = unicode(rel_path)

        # Ordner durchsuchen und Filme in Liste verstauen

        # Verzweigung für erste Iteration (hier ist der volle Pfad identisch mit dem base_path)
        if len(rel_path) > 0:
            fullpath = os.path.join(base_path, rel_path)
        else:
            fullpath = base_path

        # Prüfen ob der Pfad existiert
        if not os.path.exists(fullpath):
            print("Der Pfad {} existiert nicht!".format(fullpath))
            return  # Beenden des Rekursionspfades

        # Falls Datei, prüfen ob FileType passt und ggf. auslesen
        if os.path.isfile(fullpath):
            film_neu = self.read_file_to_film(fullpath)
            if film_neu:
                filme.append(film_neu)

        # Falls Ordner, diesen ausgeben und weitere Rekursion der Inhalte
        elif os.path.isdir(fullpath):

            # Inhalte des Ordners behandeln
            try:
                contents = os.listdir(fullpath)
            except Exception as e:
                print("Auf die Inhalte von {} kann nicht zugegriffen werden!\nFehlermeldung: {}".format(fullpath, e))
                return  # Beenden des Rekursionspfades

            for item in contents:

                # Falls option aktiv, dass Subfolder auch durchsucht werden sollen oder basisfolder
                if crawl_subfolders or (fullpath == base_path):
                    neue_filme = self.crawl_folder(base_path, crawl_subfolders, os.path.join(rel_path, item))

                    if neue_filme:
                        for film_neu in neue_filme:
                            filme.append(film_neu)

        print filme # ToDo: print Entfernen, ist nur zum Testen, ob und/oder wie die Dateien eingelesen werden
        return filme

    def read_file_to_film(self, path):
        """
        Nimmt eine Datei entgegen und liefert, falls es sich um einen Film handelt,
        ein Film-Objekt zurück. Anderenfalls None
        
        :param path: Pfad zur Datei 
        :return: Film oder None
        """
        # Dateiendung prüfen und dabei FileType ermitteln
        path_folder, filename = os.path.split(path)
        file_root, file_extension = os.path.splitext(filename)
        filetype = FileType.get_by_extension(file_extension.lower())

        if not filetype:
            return None

        # Eigenschaften auslesen
        # Genre = Null, falls nicht in Metadaten vorhanden
        film_aus_db = Film.get_by_path(path)
        if film_aus_db:
            # Ein Film mit diesem Pfad existiert bereits in der DB
            if film_aus_db.checksum_changed():
                # Checksum neu setzen
                film_aus_db.set_checksum(film_aus_db.md5(path))
                film_aus_db.set_status(1) # Status auf "geänderte Datei" setzen / ggf. später auch Metadaten neu lesen
                Film.get_cache().persist(film_aus_db)
            return film_aus_db

        # Falls der Film noch nicht in der Datenbank war
        film_neu = Film(None, file_root, path_folder, filename, Film.md5(path), None, filetype)

        return film_neu


