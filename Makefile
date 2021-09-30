build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

bash:
	docker-compose run web /bin/bash

migrations:
	docker-compose run web python manage.py makemigrations

migrate:
	docker-compose run web python manage.py migrate

superuser:
	docker-compose run web python manage.py createsuperuser 

requirements:
	poetry export -f requirements.txt --output requirements.txt

check-black:
	black --check .

check-isort:
	isort --check .

check-flake8:
	flake8
