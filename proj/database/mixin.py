from weakref import ref

from proj.database.database_manager import DatabaseManager


class DatabaseMixin:
    """
    A mixin to add access to the database from inside the API resources.
    """

    @classmethod
    def setup(cls, web_app):
        # Create a reference to the DatabaseManager
        cls._db = ref(web_app.db)
        return cls

    @property
    def db(self) -> DatabaseManager:
        # Get the value from the DatabaseManager reference
        return self._db()
