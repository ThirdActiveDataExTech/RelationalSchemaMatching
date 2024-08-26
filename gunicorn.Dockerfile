ARG PYTHON_VERSION=3.9.13

FROM python:${PYTHON_VERSION}-slim as requirements

# Make requirements.txt file from poetry dependencies
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock /
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without=test,lint --with=gunicorn

FROM python:${PYTHON_VERSION}-slim as build

# Copy requirements.txt from requirements stage and install libraries
COPY --from=requirements /requirements.txt ./requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

FROM python:${PYTHON_VERSION}-slim as gunicorn-runtime

# Setting home directory and user name
ENV APP_HOME=/home/wisenut/app
ENV GROUP_NAME=wisenut
ENV APP_USER=wisenut

# Create a non-root user and group
RUN groupadd -r $GROUP_NAME && useradd -r -g $GROUP_NAME -d $APP_HOME $APP_USER

# Set the working directory
WORKDIR $APP_HOME
RUN chown -R $APP_USER:$GROUP_NAME $APP_HOME

# Set environment variables
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=$APP_HOME:${PYTHONPATH}

# Copy installed Python packages from the build stage
COPY --from=build /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=build /usr/local/bin /usr/local/bin

# Make gunicorn worker process temp file directory
RUN mkdir -p /tmp/shm && mkdir /.local && chown -R $APP_USER:$GROUP_NAME $APP_HOME /tmp/shm /.local

# Switch to the non-root user
USER $APP_USER

# Copy necessary files and directory
COPY pyproject.toml version_info.py .env gunicorn.conf.py ./
COPY ./static ./static/
COPY ./app ./app/

# Expose the port
EXPOSE 8000

# Run the app: gunicorn (config: gunicorn.conf.py)
ENTRYPOINT ["gunicorn", "app.main:app"]