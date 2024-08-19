FROM python:3.9.13-slim as requirements-stage

RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock /
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without=test,lint --with=gunicorn

FROM python:3.9.13-slim

# Set environment variables
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/home/wisenut/app:${PYTHONPATH}

# Install libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata

# Set the working directory
WORKDIR /home/wisenut/app

# Copy requirements.txt install libraries
COPY --from=requirements-stage /requirements.txt ./requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

# Make gunicorn worker process temp file directory
RUN mkdir -p /tmp/shm && mkdir /.local

# Copy necessary files and directory
COPY pyproject.toml version_info.py .env gunicorn.conf.py ./
COPY ./static ./static/
COPY ./app ./app/


# Expose the port
EXPOSE 8000

# Run the app: gunicorn (config: gunicorn.conf.py)
ENTRYPOINT ["gunicorn", "app.main:app"]