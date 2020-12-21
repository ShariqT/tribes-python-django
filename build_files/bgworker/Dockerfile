FROM debian:buster
RUN apt-get update 
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install django
RUN pip3 install channels
RUN pip3 install django-extensions
WORKDIR /tribes
COPY ./tribes .
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=tribes_django.settings
RUN pip3 install -r ./tribes_core/requirements.txt
