ARG VERSION_BUILD

FROM python:3.12-slim-bookworm AS python
ENV PYTHONUNBUFFERED=true
WORKDIR /app

LABEL org.opencontainers.image.source=https://github.com/sdsc-ordes/gimie
LABEL org.opencontainers.image.description="Extract linked metadata from repositories."
LABEL org.opencontainers.image.licenses=Apache-2.0
LABEL org.opencontainers.image.version=${VERSION_BUILD}

##################################################
# Poetry setup
##################################################
FROM python AS poetry

# Install poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -

# Copy necessary files only
COPY gimie ./gimie
COPY pyproject.toml ./pyproject.toml
COPY poetry.lock ./poetry.lock
COPY .env.dist ./.env.dist
COPY README.md ./README.md
RUN apt-get update && \
    apt-get install -y gcc

# Poetry install
RUN poetry install --no-interaction --no-ansi -vvv


##################################################
# Gimie setup
##################################################
FROM python AS runtime
ENV PATH="/app/.venv/bin:$PATH"
RUN apt-get update && \
    apt-get install -y git libgomp1 libmagic-dev
COPY --from=poetry /app /app
COPY ".docker/entrypoint.sh" "/entrypoint.sh"

# Set user
RUN useradd -ms /bin/bash gimie_user
USER gimie_user

# Test gimie
RUN gimie --version

# Set command and entrypoint
CMD ["gimie"]
ENTRYPOINT ["/entrypoint.sh"]
