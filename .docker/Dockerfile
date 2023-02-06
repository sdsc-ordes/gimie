FROM python:3.10-slim-bullseye as python
ENV PYTHONUNBUFFERED=true
WORKDIR /app

##################################################
# Poetry setup
##################################################
FROM python as poetry

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

# Poetry install
RUN poetry install --no-interaction --no-ansi -vvv


##################################################
# Gimie setup
##################################################
FROM python as runtime
ENV PATH="/app/.venv/bin:$PATH"
RUN apt-get update && apt-get install -y git
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
