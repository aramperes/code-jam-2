from weakref import ref

from flask.views import MethodView

from proj.database.mixin import DatabaseMixin


class BaseView(MethodView, DatabaseMixin):
    """
    A class combining the Flask View and the RethinkDB mixin.
    All resources should extend this class to be registered in the WebApp.
    """
    url = ""
    name = ""

    @classmethod
    def setup(cls, web_app):
        super(BaseView, cls).setup(web_app)
        cls._web_app = ref(web_app)
        return cls

    @property
    def web_app(self):
        return self._web_app()
