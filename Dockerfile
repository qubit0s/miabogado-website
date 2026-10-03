FROM ghcr.io/nginx/nginx-unprivileged:1.30.5-alpine-slim@sha256:e28dcf0a161ddcbf228c7364b4a14f9bad4763ae8f5317c437b896afa3df4b84
USER root
RUN apk upgrade --no-cache pcre2
USER 101
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY public/ /usr/share/nginx/html/
ENTRYPOINT ["nginx", "-g", "daemon off;"]
CMD []
