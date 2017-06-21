# -*- coding: utf-8 -*-

from .database.Movie import Movie

import os


class FilmCrawler:
    def __init__(self):
        pass

    @staticmethod
    def crawl_folder(base_path, crawl_subfolders=False, rel_path=""):
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
            film_neu = Movie.read_file_to_film(fullpath)
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
                    neue_filme = FilmCrawler.crawl_folder(base_path, crawl_subfolders, os.path.join(rel_path, item))

                    # Falls neue Filme gefunden wurden, werden diese der Liste hinzugefügt
                    if neue_filme:
                        for film_neu in neue_filme:
                            filme.append(film_neu)

        print(filme) # ToDo: print Entfernen, ist nur zum Testen, ob und/oder wie die Dateien eingelesen werden
        return filme



