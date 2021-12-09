build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

web = docker-compose run --rm --no-deps web

bash:
	$(web) /bin/bash

shell:
	$(web) python manage.py shell

migrations:
	$(web) python manage.py makemigrations

empty-migration:
	$(web) python manage.py makemigrations --empty $(app)

migrate:
	$(web) python manage.py migrate

groups:
	$(web) python manage.py create_groups

test-data: groups
	$(web) python manage.py loaddata test-users.json
	$(web) python manage.py loaddata test-chartofaccount.json

first-use:
	docker-compose down
	$(web) python manage.py migrate
	$(web) python manage.py create_groups
	$(web) python manage.py loaddata test-users.json
	$(web) python manage.py loaddata test-chartofaccount.json
	docker-compose up

superuser:
	$(web) python manage.py createsuperuser

poetry-lock:
	$(web) poetry lock --no-update

requirements:
	$(web) poetry export -f requirements.txt --output requirements.txt --without-hashes

check-black:
	$(web) black --check .

check-isort:
	$(web) isort --check .

check-flake8:
	$(web) flake8 $(file)

check-migrations:
	$(web) python manage.py makemigrations --check

check: check-black check-isort check-flake8 check-migrations

test:
	docker-compose run --rm web pytest

test-create-db:
	docker-compose run --rm web pytest --create-db

collectstatic:
	$(web) python manage.py collectstatic

compilescss:
	$(web) python manage.py compilescss

black:
	black .

isort:
	isort .

all-formatters: isort black
