FROM ghcr.io/nginx/nginx-unprivileged:1.31.6-alpine-slim@sha256:c81a27f28bc2d9c2da8998444e653c7b85b9bbbaa92e44ef18d8920784e06507
USER root
RUN apk upgrade --no-cache pcre2
USER 101
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY public/ /usr/share/nginx/html/
ENTRYPOINT ["nginx", "-g", "daemon off;"]
CMD []
