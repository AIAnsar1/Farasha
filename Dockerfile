FROM python:3.12-slim-bullseye as build
WORKDIR /Farisha

RUN pip3 install --no-cache-dir --upgrade pip

FROM python:3.12-slim-bullseye
WORKDIR /Farisha

ARG VCS_REF= # CHANGE ME ON UPDATE
ARG VCS_URL="https://github.com/AiAnsar1/Farisha"
ARG VERSION_TAG= # CHANGE ME ON UPDATE

ENV Farisha_ENV=docker

LABEL org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url=$VCS_URL \
      org.label-schema.name="Farisha" \
      org.label-schema.version=$VERSION_TAG \
      website="https://sherlockproject.xyz"

RUN pip3 install --no-cache-dir Farisha==$VERSION_TAG

WORKDIR /Farisha

ENTRYPOINT ["Farisha"]