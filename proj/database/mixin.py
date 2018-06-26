from weakref import ref

from proj.database.database_manager import DatabaseManager


class DatabaseMixin:
    """
    A mixin to add access to the database from inside resources.
    """

    @classmethod
    def setup(cls, web_app):
        cls._db = ref(web_app.db)
        return cls

    @property
    def db(self) -> DatabaseManager:
        return self._db()
