build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

bash:
	docker-compose run --rm web /bin/bash

migrations:
	docker-compose run --rm web python manage.py makemigrations

migrate:
	docker-compose run --rm web python manage.py migrate

superuser:
	docker-compose run --rm web python manage.py createsuperuser

requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

black:
	black --check .

isort:
	isort --check .

flake8:
	flake8

collectstatic:
	docker-compose run --rm web python manage.py collectstatic

compilescss:
	docker-compose run --rm web python manage.py compilescss
