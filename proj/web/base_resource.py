from weakref import ref

from flask_restful import Resource

from proj.database.mixin import DatabaseMixin


class BaseResource(Resource, DatabaseMixin):
    """
    A class combining the Flask-RESTful Resource and the RethinkDB mixin.
    """
    url = ""
    name = ""

    @classmethod
    def setup(cls, web_app):
        super(BaseResource, cls).setup(web_app)
        cls._web_app = ref(web_app.db)
        return cls

    @property
    def web_app(self):
        return self._web_app()
