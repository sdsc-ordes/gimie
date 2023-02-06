FROM python:3.10-slim-bullseye as python
ENV PYTHONUNBUFFERED=true
WORKDIR /app


FROM python as poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -
COPY . ./
RUN poetry install --no-interaction --no-ansi -vvv


FROM python as runtime
ENV PATH="/app/.venv/bin:$PATH"
RUN apt-get update && apt-get install -y git
COPY --from=poetry /app /app
RUN gimie --help
COPY ".docker/entrypoint.sh" "/entrypoint.sh"
RUN useradd -ms /bin/bash gimie_user
USER gimie_user

CMD ["gimie"]
ENTRYPOINT ["/entrypoint.sh"]

