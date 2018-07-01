import io
import logging
import os
import random
import subprocess

import markovify
import rethinkdb
from ffmpy import FFmpeg
from flask import request
from gtts import gTTS
from werkzeug.exceptions import Forbidden, ServiceUnavailable

from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth

log = logging.getLogger(__name__)


class CreateStoryResource(BaseResource):
    name = "api.stories.create"
    url = "/story"

    @oauth(force=True)
    def post(self):
        # first of all, check if the user has reached their quota
        if not self.web_app.debug:
            quota = int(self.web_app.config.get("stories", "max_story_count", default=10))
            stories_query = self.db.query("stories").get_all(
                self.user_data["id"], index="user_id").pluck().limit(quota).count()
            count = self.db.run(stories_query)
            if count >= quota:
                raise Forbidden(description="You have exceeded your quota of {0} stories. "
                                            "Use the 'DELETE /story/<story_id>' to clean up your stories."
                                .format(quota))

        data = request.json or {}
        # optional parameter: public (true/false), default true
        # optional parameter: music (true/false), default true
        # optional parameter: video (true/false), default true

        public = bool(data.get("public", True))
        music = bool(data.get("music", True))
        video = bool(data.get("video", True))

        # Generate some sentences from a corpus, using markov chains (woo, how original)
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

        if not music and not video:
            # no FFMPEG filtering necessary
            media_output = tts_binary
        else:
            # Music parameters
            music_path = os.path.join(".", "assets", "music", "track.mp3")
            music_time_start = random.randrange(0, 1200)  # seconds
            music_volume = 0.2

            # FFMPEG filters
            if music and video:
                # Mix music, TTS, and video
                # 1. First, the volume of the music track is reduced, while the TTS track is left at 100%
                # 2. Then, the audio of the music track is trimmed to start at a certain time
                # 3. Finally, the two audio tracks are mixed together to produce one track
                # 4. Duplicate the mixed audio track into two labels
                # 5. Generate a video with the samples waves from the first audio label
                # 6. Export video and audio to pipe in webm format
                ffmpeg_filter = "-filter_complex " \
                                "[0:a]volume=1[a0];[1:a]volume={music_volume}[a1];" \
                                "[a1]atrim=start={music_start}[a1];" \
                                "[a0][a1]amix=inputs=2:duration=shortest:dropout_transition=3[a];" \
                                "[a]asplit[outa1][outa2];" \
                                "[outa1]showwaves=s=1280x202:mode=line[sw]" \
                                " -map \"[sw]\" -map \"[outa2]\" -c:v libvpx -auto-alt-ref 0 -speed 8 " \
                                "-c:a libvorbis -f webm" \
                    .format(music_start=music_time_start,
                            music_volume=music_volume)
                ff_inputs = {
                    "pipe:0": None,
                    music_path: None
                }

            elif music:
                # Mix music and TTS
                # 1. First, the volume of the music track is reduced, while the TTS track is left at 100%
                # 2. Then, the audio of the music track is trimmed to start at a certain time
                # 3. Finally, the two audio tracks are mixed together to produce one track
                # 4. Export to pipe in MP3
                ffmpeg_filter = "-filter_complex " \
                                "[0:a]volume=1[a0];[1:a]volume={music_volume}[a1];" \
                                "[a1]atrim=start={music_start}[a1];" \
                                "[a0][a1]amix=inputs=2:duration=shortest:dropout_transition=3[a]" \
                                " -map \"[a]\" -f mp3".format(music_start=music_time_start,
                                                              music_volume=music_volume)
                ff_inputs = {
                    "pipe:0": None,
                    music_path: None
                }

            else:
                # Mix video and TTS
                # 1. The TTS audio track is duplicated into two labels
                # 2. Generate a video with the samples waves from the first audio label
                # 3. Export video and audio to pipe in webm format
                ffmpeg_filter = "-filter_complex " \
                                "[0:a]asplit[outa1][outa2];" \
                                "[outa1]showwaves=s=1280x202:mode=line[sw]" \
                                " -map \"[sw]\" -map \"[outa2]\" -c:v libvpx -auto-alt-ref 0 -speed 8 " \
                                "-c:a libvorbis -f webm"
                ff_inputs = {
                    "pipe:0": None
                }

            # Launch ffmpeg
            ff = FFmpeg(
                executable=self.web_app.config.get("stories", "ffmpeg"),
                inputs=ff_inputs,
                outputs={
                    "pipe:1": ffmpeg_filter
                }
            )
            log.debug("Executing FFMPEG command: {0}".format(ff.cmd))
            # The mixed track is output using the subprocess's STDOUT, piped to the mixed_bytes var
            media_output, stderr = ff.run(input_data=tts_binary, stdout=subprocess.PIPE)
            if stderr:
                log.debug("FFMPEG STDERR: %s", str(stderr.read()))
            else:
                log.debug("No FFMPEG STDERR")

        # store in database
        story_insert_doc = {
            "public": public,
            "user_id": self.user_data["id"],
            "sentences": sentences,
            "media": rethinkdb.binary(media_output),
            "media_type": "video/webm" if video else "audio/mpeg"
        }
        insert_query = self.db.query("stories").insert(story_insert_doc)
        story_id = self.db.run(insert_query)["generated_keys"][0]

        story_query = self.db.query("stories").get(story_id).pluck("id", "public", "sentences")
        story = self.db.run(story_query)
        story["media"] = "/story/{0}/play".format(story_id)
        story["url"] = "/story/{0}".format(story_id)
        return story
