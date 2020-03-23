FROM alpine:3.11.2

ADD requirements.txt requirements.txt
RUN apk add --no-cache python3 libmagic \
    && pip3 install -r requirements.txt \
    && rm -r requirements.txt /root/.cache
ADD app app

ENTRYPOINT ["flask", "run"]
