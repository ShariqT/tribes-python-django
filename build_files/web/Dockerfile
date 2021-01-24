FROM debian:buster
RUN apt-get update 
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y ruby
RUN apt-get install -y ruby-dev
RUN gem install jekyll bundler
RUN pip3 install django
RUN pip3 install channels
RUN pip3 install django-extensions
VOLUME /tribes
WORKDIR /tribes
COPY ./tribes .
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=tribes_django.settings
RUN pip3 install -r ./tribes_core/requirements.txt
RUN python3 manage.py migrate
RUN python3 manage.py collectstatic --noinput