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
        raise NotImplementedError

    def persist(self, obj):
        obj.persist()
        self.instances[obj.db_id] = obj

    def delete(self, obj):
        if obj.db_id:
            obj.delete()
            del self.instances[obj.db_id]
        else:
            raise AssertionError("Die Id des Objekts darf nicht 'None' sein!")