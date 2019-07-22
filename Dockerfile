FROM python:3.7-alpine3.9

ENV OJ_ENV production

RUN apk add --update --no-cache build-base nginx openssl curl unzip supervisor jpeg-dev zlib-dev postgresql-dev freetype-dev

ADD ./deploy/requirements.txt /app/deploy/requirements.txt

RUN pip install --no-cache-dir -r /app/deploy/requirements.txt && apk del build-base --purge

ADD . /app
WORKDIR /app

HEALTHCHECK --interval=5s --retries=3 CMD python2 /app/deploy/health_check.py


#RUN curl -L  $(curl -s  https://api.github.com/repos/QingdaoU/OnlineJudgeFE/releases/latest | grep /dist.zip | cut -d '"' -f 4) -o dist.zip && \
#    unzip dist.zip && \
#    rm dist.zip

ENTRYPOINT /app/deploy/entrypoint.sh
