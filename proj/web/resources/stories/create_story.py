import io
import os
import subprocess

import markovify
import rethinkdb
from ffmpy import FFmpeg
from flask import request
from gtts import gTTS
from werkzeug.exceptions import ServiceUnavailable

from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth


class CreateStoryResource(BaseResource):
    name = "api.stories.create"
    url = "/story"

    @oauth(force=True)
    def post(self):
        data = request.json or {}
        # optional parameter: public (true/false), default true
        # optional parameter: music (true/false), default true

        public = bool(data.get("public", True))
        music = bool(data.get("music", True))

        corpus_path = os.path.join(".", "assets", "texts", "texts.txt")
        if not os.path.exists(corpus_path):
            raise ServiceUnavailable(description="Corpus is unavailable.")

        with open(corpus_path) as corpus_file:
            corpus = corpus_file.read()

        model = markovify.Text(corpus)

        sentences = []
        for i in range(10):
            if i is 0:
                sentence = model.make_sentence_with_start(beginning="Once", strict=False)
            else:
                sentence = model.make_sentence()
            if sentence:
                sentences.append(sentence)

        # Use TTS to recite the text
        tts = gTTS(text=" ".join(sentences), lang="en")
        with io.BytesIO() as tts_buffer:
            # Write the TTS result to the buffer
            tts.write_to_fp(tts_buffer)
            # Bring back the cursor to the beginning of the buffer
            tts_buffer.seek(0)
            # Read the buffer
            tts_binary = tts_buffer.read()

        if music:
            music_path = os.path.join(".", "assets", "music", "track.mp3")
            # todo: randomize music start
            music_time_start = 100  # seconds

            # The syntax may look intimidating at first, but simply this applies 3 filters to the 2 audio tracks:
            # 1. First, the volume of the music track is reduced to 10%, while the TTS track is left at 100%
            # 2. Then, the audio of the music track is trimmed to start at a certain time
            # 3. Finally, the two audio tracks are mixed together to produce one track
            ffmpeg_filter = "-filter_complex " \
                            "[0:a]volume=1[a0];[1:a]volume=0.1[a1];" \
                            "[a1]atrim=start={music_start}[a1];" \
                            "[a0][a1]amix=inputs=2:duration=shortest:dropout_transition=3[a]" \
                            " -map \"[a]\" -f mp3".format(music_start=music_time_start)

            # The first track (TTS) is piped from the stream
            # The second track (music) is read from file by FFMPEG
            ff = FFmpeg(
                executable=self.web_app.config.get("stories", "ffmpeg"),
                inputs={
                    "pipe:0": None,
                    music_path: None
                },
                outputs={
                    "pipe:1": ffmpeg_filter
                }
            )
            # The mixed track is output using the subprocess's STDOUT, piped to the mixed_bytes var
            mixed_bytes, stderr = ff.run(input_data=tts_binary, stdout=subprocess.PIPE)
            media_output = mixed_bytes
        else:
            media_output = tts_binary

        # store in database
        story_insert_doc = {
            "public": public,
            "user_id": self.user_data["id"],
            "sentences": sentences,
            "media": rethinkdb.binary(media_output)
        }
        insert_query = self.db.query("stories").insert(story_insert_doc)
        story_id = self.db.run(insert_query)["generated_keys"][0]

        story_query = self.db.query("stories").get(story_id).pluck("id", "public", "sentences")
        story = self.db.run(story_query)
        story["media"] = "/story/{0}/play".format(story_id)
        story["url"] = "/story/{0}".format(story_id)
        return story
