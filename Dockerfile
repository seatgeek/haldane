FROM python:2-onbuild

RUN pip install greenlet gevent gunicorn honcho

RUN pip install ./

CMD [ "honcho", "start" ]
