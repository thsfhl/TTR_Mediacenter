# -*- coding: utf-8 -*-

from .FileType import FileType
import os

class FilmCrawler:

    def __init__(self):
        pass

    @staticmethod
    def crawl_folder(rootpath, rel_path, crawl_subfolders = False):
        """
        Sucht Dateien innerhalb des übergebenen Pfades aus und ruft sich selbst
        für jeden Eintrag auf, der wiederum ein Ordner ist, falls crawl_subfolder == true

        Je passt die Dateiendung zu einer der Endungen in "FileType", wird die Datei
        ausgelesen, in ein Film-Objekt umgewandelt und dann im Array zurückgegeben.

        :param base_path: Basispfad, der beim ersten Aufruf angegeben wird
        :param rel_path: Relativer Pfad des Elements zum Basispfad
        :return: Kein Rückgabewert, sondern Ausgabe auf der Konsole
        """

        filme = []

        # Ordner durchsuchen und Filme in Liste verstauen

        # Verzweigung für erste Iteration
        if len(rel_path) > 0:
            fullpath = os.path.join(rootpath, rel_path)
        else:
            fullpath = rootpath

        # Prüfen ob der Pfad existiert
        if not os.path.exists(fullpath):
            print("Der Pfad {} existiert nicht!".format(fullpath))
            return  # Beenden des Rekursionspfades

        # Falls Datei, prüfen ob FileType passt und ggf. auslesen
        if os.path.isfile(fullpath):
            # ToDo: Prüfen der Dateiendung und Auslesen der Dateiinfos
            raise NotImplementedError

        # Falls Ordner, diesen ausgeben und weitere Rekursion der Inhalte
        elif os.path.isdir(fullpath):

            # Inhalte des Ordners behandeln
            try:
                contents = os.listdir(fullpath)
            except Exception as e:
                print("Auf die Inhalte von {} kann nicht zugegriffen werden!\nFehlermeldung: {}".format(fullpath, e))
                return  # Beenden des Rekursionspfades

            for item in contents:
                # ToDo: Items lesen
                raise NotImplementedError

        return filme

