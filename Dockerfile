FROM ghcr.io/nginx/nginx-unprivileged:1.30.5-alpine-slim@sha256:3af0c10d960cc2502427fe1219c52989d309e7d65596869c60a34fd2fa2406f0
USER root
RUN apk upgrade --no-cache pcre2
USER 101
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY public/ /usr/share/nginx/html/
ENTRYPOINT ["nginx", "-g", "daemon off;"]
CMD []
