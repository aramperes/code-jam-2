from flask_restful import Resource

from proj.database.mixin import DatabaseMixin


class BaseResource(Resource, DatabaseMixin):
    """
    A class combining the Flask-RESTful Resource and the RethinkDB mixin.
    """
    url = ""
    name = ""
