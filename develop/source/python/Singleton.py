# -*- coding: utf-8 -*-


def singleton(cls):
    """ Decorator für Klassen, die als Singleton fungieren sollen """

    # Liste der Instanzen
    instances = {}

    def getinstance():
        """
        Falls eine Instanz dieser Klasse existiert, wird beim "Erzeugen" eines
        neuen Objekts das bestehende Objekt zurückgegeben.
        """
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    # Die Methode getinstance wird zurückgegeben
    return getinstance

