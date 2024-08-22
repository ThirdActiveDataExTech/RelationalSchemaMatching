FROM python:3.9.13-slim as requirements

# Make requirements.txt file from poetry dependencies
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock /
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without=test,lint,gunicorn

FROM python:3.9.13-slim as build

# Copy requirements.txt from requirements stage and install libraries
COPY --from=requirements /requirements.txt ./requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

FROM python:3.9.13-slim as prod-runtime

# Setting home directory and user name
ENV APP_HOME=/home/wisenut/app
ENV GROUP_NAME=wisenut
ENV APP_USER=wisenut

# Create a non-root user and group
RUN groupadd -r $GROUP_NAME && useradd -r -g $GROUP_NAME -d $APP_HOME $APP_USER

# Set the working directory
WORKDIR $APP_HOME
RUN chown -R $APP_USER:$GROUP_NAME $APP_HOME

# Switch to the non-root user
USER $APP_USER

# Set environment variables
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=$APP_HOME:${PYTHONPATH}

# Copy installed Python packages from the build stage
COPY --from=build /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=build /usr/local/bin /usr/local/bin

# Copy necessary files and directory
COPY pyproject.toml version_info.py .env ./
COPY ./static ./static/
COPY ./app ./app/

# Expose the port
EXPOSE 8000

# Run the app
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]