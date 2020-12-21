FROM debian:buster
RUN apt-get update
RUN apt-get install -y nginx
RUN apt-get install -y libnginx-mod-rtmp
COPY ./build_files/nginx/default /etc/nginx/sites-available
COPY ./LOCAL_STATIC /var/www/html/static
EXPOSE 80
