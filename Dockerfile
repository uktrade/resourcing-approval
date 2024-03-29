FROM python:3.10-buster

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONSTARTUP=.pythonrc.py
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install poetry

COPY poetry.lock pyproject.toml /app/

RUN poetry install

COPY . /app/

CMD python manage.py runserver 0.0.0.0:8000
