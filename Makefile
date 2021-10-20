build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

web = docker-compose run --rm web

bash:
	$(web) /bin/bash

shell:
	$(web) python manage.py shell

migrations:
	$(web) python manage.py makemigrations

migrate:
	$(web) python manage.py migrate

groups:
	$(web) python manage.py loaddata groups.json

test-data: groups	
	$(web) python manage.py loaddata test-users.json

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

flake8:
	$(web) flake8 $(file)

collectstatic:
	$(web) python manage.py collectstatic

compilescss:
	$(web) python manage.py compilescss
