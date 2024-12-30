ARG IMAGE=registry.gitlab.com/wisenut-research/research/2024-iitp-3rd-party-data/column-to-column-correlation-analysis-service
ARG VARIANT=cpu
FROM ${IMAGE}:deps-${VARIANT} AS builder

FROM python:3.11-slim AS production

ENV USER=wisenut \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/.venv

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN useradd -m -s /bin/bash $USER

WORKDIR /home/$USER

COPY --from=builder /app/.venv $VIRTUAL_ENV

COPY --chown=$USER:$USER static ./static
COPY --chown=$USER:$USER model ./model
COPY --chown=$USER:$USER test_data ./test_data
COPY --chown=$USER:$USER app ./app

USER $USER

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]