import glob
import os

from proj.web.api.base_resource import BaseResource


class ListCorpusStoriesResource(BaseResource):
    name = "api.stories.corpus"
    url = "/stories/corpus"

    def get(self):
        return list_corpus()


def list_corpus():
    # all available corpus
    corpus_dir = os.path.join(".", "assets", "texts")
    corpus_glob = os.path.join(corpus_dir, "*.txt")
    corpus_list = [os.path.splitext(os.path.basename(path))[0] for path in glob.glob(corpus_glob)]
    return corpus_list
