ARG VERSION_BUILD

FROM python:3.12-slim-bookworm AS python
ENV PYTHONUNBUFFERED=true
WORKDIR /app

LABEL org.opencontainers.image.source=https://github.com/sdsc-ordes/gimie
LABEL org.opencontainers.image.description="Extract linked metadata from repositories."
LABEL org.opencontainers.image.licenses=Apache-2.0
LABEL org.opencontainers.image.version=${VERSION_BUILD}

##################################################
# Build stage
##################################################
FROM python AS build

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy necessary files only
COPY gimie ./gimie
COPY pyproject.toml ./pyproject.toml
COPY uv.lock ./uv.lock
COPY .env.dist ./.env.dist
COPY README.md ./README.md
RUN apt-get update && \
    apt-get install -y gcc

# Install dependencies
RUN uv sync --no-dev -v

##################################################
# Gimie setup
##################################################
FROM python AS runtime
ENV PATH="/app/.venv/bin:$PATH"
RUN apt-get update && \
    apt-get install -y git libgomp1 libmagic-dev
COPY --from=build /app /app
COPY ".docker/entrypoint.sh" "/entrypoint.sh"

# Set user
RUN useradd -ms /bin/bash gimie_user
USER gimie_user

# Test gimie
RUN gimie --version

# Set command and entrypoint
CMD ["gimie"]
ENTRYPOINT ["/entrypoint.sh"]
