FROM nginx:alpine

# Install necessary packages for RTMP module
RUN apk add --no-cache --virtual .build-deps \
    build-base \
    libressl-dev \
    pcre-dev \
    zlib-dev \
    curl \
    git \
    && git clone https://github.com/sergey-dryabzhinsky/nginx-rtmp-module.git \
    && cd /tmp \
    && curl -LO https://nginx.org/download/nginx-1.21.6.tar.gz \
    && tar xzf nginx-1.21.6.tar.gz \
    && cd nginx-1.21.6 \
    && ./configure \
        --add-module=/nginx-rtmp-module \
        --conf-path=/etc/nginx/nginx.conf \
        --with-http_ssl_module \
    && make \
    && make install \
    && apk del .build-deps \
    && rm -rf /tmp/*

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 1935 80
CMD ["nginx", "-g", "daemon off;"]
