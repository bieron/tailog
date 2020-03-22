FROM alpine:3.11.2

ADD requirements.txt requirements.txt
RUN apk add python3 libmagic \
    && pip3 install -r requirements.txt \
    && rm requirements.txt
ADD app app

ENTRYPOINT ["flask", "run"]
