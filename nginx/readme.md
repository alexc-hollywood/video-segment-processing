# Build & Deploy

```
docker build -t <your_docker_hub_username>/nginx-rtmp:latest .
docker push <your_docker_hub_username>/nginx-rtmp:latest
```

## Deploy

```
kubectl apply -f deployment.yaml
```

## Configure Load Balancer
Since the Service is of type LoadBalancer, Kubernetes will provision a cloud load balancer that automatically distributes traffic to the nginx-rtmp instances. The load balancer listens on both RTMP (port `1935`) and HTTP (port `80`) for incoming connections.

## Scaling and Monitoring
You can use Kubernetes features like autoscaling and resource limits to scale the number of nginx-rtmp instances according to the load. Furthermore, you can monitor the health and performance of your instances using Kubernetes-native tools or third-party solutions.


# Access from OBS Studio

To publish a live stream from OBS Studio, follow these steps:

## Download and install OBS Studio
Download the appropriate version of OBS Studio for your operating system from the official website: https://obsproject.com/download. Install the software following the instructions for your operating system.

In the "Sources" box at the bottom of the window, click the "+" button and choose the source you want to stream. For example, if you want to stream your display, choose "Display Capture" and select the desired display. You can add multiple sources, such as webcam, audio input, or text.

Click on "Settings" in the lower right corner of the window.

Go to the "Output" tab. Set the "Output Mode" to "Advanced", and then select the "Streaming" tab. Adjust the settings as needed. For example, you can set the video bitrate to control the quality and size of your video stream. The recommended video bitrate for a 1080p video is between `3000` and `6000` Kbps.

Go to the "Audio" tab and select the appropriate audio devices for your microphone and speakers or other audio sources.

Set up the streaming server
To stream to the nginx-rtmp server you configured in Kubernetes, go to the "Stream" tab in the "Settings" window:

Set the "Stream Type" to "Custom Streaming Server".

In the "URL" field, enter the RTMP URL of your load balancer, using the format `rtmp://<load_balancer_ip_or_hostname>/live`. Replace `<load_balancer_ip_or_hostname>` with the IP address or hostname of your load balancer.

In the "Stream key" field, enter a unique identifier for your stream, such as "mystream". This identifier will be used in the HLS and DASH URLs to access your stream.

# Stream and Access Content
Now, you can use an RTMP streaming client like OBS Studio to publish your live stream to the load balancer's IP address or hostname on port 1935, using the live application.

To access the streams, you can use the following URLs:

- HLS: `http://<load_balancer_ip_or_hostname>/hls/<stream_key>.m3u8`
- DASH: `http://<load_balancer_ip_or_hostname>/dash/<stream_key>.mpd`

Replace `<load_balancer_ip_or_hostname>` with the IP address or hostname of your load balancer, and `<stream_key>` with the stream key you used in your streaming client.

# Security

## Authentication

To secure the RTMP connection with a shared secret by adding a simple authentication mechanism in the nginx.conf file:

```
rtmp {
    ...
    application live {
        ...
        on_publish http://localhost:8080/auth;
    }
}
```

Then, create a simple authentication server, e.g., using Node.js and Express, to validate the stream key and the shared secret provided by the publisher. This server will listen on port `8080` and return a `200` status code if the credentials are valid, or a `401` status code otherwise.

## Encryption

We can serve HLS and DASH streams over HTTPS to encrypt the data transmitted between the server and the client.

To enable HTTPS, you will need an SSL/TLS certificate for your domain. You can obtain a certificate from a Certificate Authority (CA) such as Let's Encrypt. Once you have the certificate, update your nginx.conf file to include the necessary configuration for HTTPS:

```
http {
    ...
    server {
        ...
        listen 443 ssl;
        ssl_certificate /path/to/your/certificate.pem;
        ssl_certificate_key /path/to/your/private_key.pem;
        ...
    }
}
```

## IP Access Control
To restrict access to the HLS and DASH streams in your nginx.conf file using the allow and deny directives:

```
http {
    ...
    server {
        ...
        location /hls {
            ...
            allow 192.168.1.0/24;
            deny all;
        }
        location /dash {
            ...
            allow 192.168.1.0/24;
            deny all;
        }
    }
}

```

This configuration allows access to the streams only from IP addresses in the 192.168.1.0/24 subnet and denies access to all other IP addresses.

## Geographic Control

To restrict access by geographic country or region in Nginx, you can use the GeoIP module. This module allows you to create access rules based on the client's IP address and associated geographic location. Follow these steps to set up the GeoIP module in Nginx:

### Install the GeoIP module

For most Linux distributions, the GeoIP module is available in the package manager. Install it using the appropriate command for your distribution:

Ubuntu/Debian: `sudo apt-get install nginx-module-geoip`
CentOS/RHEL: `sudo yum install nginx-module-geoip`

### Enable the GeoIP module

Edit your Nginx configuration file, usually located at `/etc/nginx/nginx.conf`. Add the following lines at the top of the file, after the first line containing user ...

```
load_module modules/ngx_http_geoip_module.so;
``` 

This line tells Nginx to load the GeoIP module. Adjust the path to the module file if necessary, depending on your Nginx installation.

### Download the GeoIP database

Download the GeoLite2 Country database from MaxMind in MMDB format:

```
wget https://github.com/maxmind/GeoIP2-php/releases/download/2.9.0/GeoLite2-Country.mmdb.gz
gunzip GeoLite2-Country.mmdb.gz
sudo mkdir -p /etc/nginx/geoip
sudo mv GeoLite2-Country.mmdb /etc/nginx/geoip/
```

### Configure GeoIP in Nginx

In your Nginx configuration file (`/etc/nginx/nginx.conf`), add the following lines inside the http block:

```
http {
    ...
    geoip_country /etc/nginx/geoip/GeoLite2-Country.mmdb;
    map $geoip_country_code $allowed_country {
        default no;
        US yes;
        CA yes;
    }
    ...
}
```

This configuration sets up the GeoIP country database and creates a map called $allowed_country. The map checks the client's country code (based on their IP address) and sets the value of $allowed_country to "yes" if the country code is "US" or "CA" (United States or Canada) and "no" otherwise.


### Restrict access by country or region

In your Nginx configuration file, within the appropriate server block and location block (e.g., /hls or /dash), add the following lines to restrict access based on the client's geographic location:

```
server {
    ...
    location /hls {
        ...
        if ($allowed_country = no) {
            return 403;
        }
    }
    location /dash {
        ...
        if ($allowed_country = no) {
            return 403;
        }
    }
}
```