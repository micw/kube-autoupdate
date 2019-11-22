FROM python:3.8-alpine AS build

RUN apk add --update --no-cache build-base python3-dev
RUN apk add --update --no-cache libffi-dev openssl-dev

ADD requirements.txt /requirements.txt
RUN pip3 install --user -r /requirements.txt

FROM python:3.8-alpine

RUN apk add --update --no-cache libffi openssl
COPY --from=build /root/.local /root/.local
ADD src/ /kube-autoupdate/

CMD /kube-autoupdate/run.py schedule
