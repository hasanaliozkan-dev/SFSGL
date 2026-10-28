FROM python:3.12-slim

COPY . /src
RUN pip install --no-cache-dir /src && rm -rf /src

# Shared files and collected submissions live here; mount it so uploads survive the container
WORKDIR /data
VOLUME /data

EXPOSE 5001 5002
CMD ["sfsgl", "--shared", "/data/shared", "--gathered", "/data/gathered"]
