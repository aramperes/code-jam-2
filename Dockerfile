FROM python:3.6.5-stretch

ENV RETHINKDB_HOST rethinkdb
ENV FFMPEG_EXEC /usr/bin/ffmpeg

WORKDIR /opt/app

ADD . .

RUN apt-get update
RUN apt-get -y install build-essential libffi-dev python-dev ffmpeg
RUN pip install pipenv
RUN pipenv sync

EXPOSE 80
CMD pipenv run python run.py
