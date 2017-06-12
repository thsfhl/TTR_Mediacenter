# -*- coding: utf-8 -*-


class ObjectCache:
    """
    Klasse cached Objekte einer Klasse, um Datenbankzugriffe zu vermeiden
    """

    def __init__(self, cls):
        self.cls = cls
        self.instances = {}

    def get_by_id(self, db_id):
        if db_id not in self.instances:
            obj = self.cls.get_by_id(db_id)
            if obj:
                self.instances[db_id] = obj
            else:
                return None

        return self.instances[db_id]

    def get_all(self):
        """" Hier sollen alle Werte aus der DB geladen und im Cache abgelegt werden """
        objs = self.cls.get_all()
        for obj in objs:
            self.instances[obj.get_db_id()] = obj

        return self.instances

    def persist(self, obj):
        obj.persist()
        self.instances[obj.get_db_id()] = obj

    def delete(self, obj):
        if obj.get_db_id():
            obj.delete()
            del self.instances[obj.get_db_id()]
        else:
            raise AssertionError("Die Id des Objekts darf nicht 'None' sein!")