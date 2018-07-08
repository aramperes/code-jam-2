from flask import render_template

from proj.web.console.base_view import BaseView


class ConsoleIndexView(BaseView):
    name = "index"
    url = "/"

    def get(self):
        return render_template(
            "./index.html"
        )
