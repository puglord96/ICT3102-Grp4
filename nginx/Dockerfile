FROM nginx

EXPOSE 80
EXPOSE 8080

RUN rm /usr/share/nginx/html/*

COPY ./nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
