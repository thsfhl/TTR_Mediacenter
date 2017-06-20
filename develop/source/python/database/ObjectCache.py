# -*- coding: utf-8 -*-


class ObjectCache:
    """
    Klasse cached Objekte einer Klasse, um Datenbankzugriffe zu vermeiden
    """

    def __init__(self, cls):
        self.cls = cls
        self.instances = {}

    def get_by_id(self, db_id):
        if db_id in self.instances:
            return self.instances[db_id]
        else:
            return None

    def get_all(self):
        """" Hier sollen alle Werte aus der DB geladen und im Cache abgelegt werden """
        objs = self.cls.get_all()
        for obj in objs:
            self.instances[obj.get_db_id()] = obj

        return self.instances

    def remove_from_cache(self, obj):
        if obj.get_db_id():
            del self.instances[obj.get_db_id()]
        else:
            raise AssertionError("Die Id des Objekts darf nicht 'None' sein!")

    def get_by_property(self, prop_name, prop_value):
        """ Holt nur Objekt aus dem Cache, ohne alternativ in der Datenbank zu suchen """
        for key, value in self.instances.items():
            if getattr(value, "_" + prop_name) == prop_value:
                return value
        return None

    def add_to_cache(self, obj):
        if obj.get_db_id():
            self.instances[obj.get_db_id()] = obj

