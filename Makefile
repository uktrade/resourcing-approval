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
	docker-compose run --rm web poetry export -f requirements.txt --output requirements.txt --without-hashes

check-black:
	docker-compose run --rm web black --check .

check-isort:
	docker-compose run --rm web isort --check .

flake8:
	docker-compose run --rm web flake8 $(file)

collectstatic:
	docker-compose run --rm web python manage.py collectstatic

compilescss:
	docker-compose run --rm web python manage.py compilescss
