from flask import render_template
from flask.views import MethodView


class LandingView(MethodView):

    def get(self):
        return render_template(
            "./landing.html"
        )
