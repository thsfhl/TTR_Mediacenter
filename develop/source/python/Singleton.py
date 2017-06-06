# -*- coding: utf-8 -*-

# Pattern für einen Singleton

def singleton(cls):
    # Liste der Instanzen
    instances = {}

    # Falls eine Instanz dieser Klasse existiert, wird beim "Erzeugen" eines
    # neuen Objekts das bestehende Objekt zurückgegeben.
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    # Die Methode getinstance wird zurückgegeben
    return getinstance

