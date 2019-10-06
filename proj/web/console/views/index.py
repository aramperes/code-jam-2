from flask import render_template

from proj.web.api.resources.stories.corpus import list_corpus
from proj.web.console.base_view import BaseView


class ConsoleIndexView(BaseView):
    name = "index"
    url = "/"

    def get(self):
        functions = {
            "list_corpus": list_corpus
        }

        return render_template(
            "./index.html", functions=functions
        )
