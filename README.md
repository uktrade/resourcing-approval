# resourcing-approval

# Local environment

## Requirements

- make
- docker
- docker-compose
- [poetry](https://python-poetry.org/docs/#installation)

## Setup

1. `git config core.hooksPath .githooks`
2. `cp .env.example .env`
3. `npm install`
4. `make build`

## Running

1. `make first-use`
2. Goto http://localhost:8000/admin and login
   - You can find the login details for test users on confluence
3. Goto http://localhost:8000

# Deployment

- If you have made any changes to the dependencies, compile the new `requirements.txt`
  file using `make requirements`.

## How to update the country list

1. Goto https://data.trade.gov.uk/datasets/240d5034-6a83-451b-8307-5755672f881b/grid
2. Click the "Download data as JSON" button (do not apply any filters)
3. Save the JSON file
4. Generate the new fixture using the `generate_countries_fixture` management command
   1. `make bash`
   2. `python manage.py generate_countries_fixture path/to/downloaded/file.json > countries/fixtures/countries.json`
5. Load the new data `python manage.py loaddata countries.json`

# Integrations

- GOV.UK Notify

# Technologies we use

## Frontend

- [GDS](https://design-system.service.gov.uk/)
- [htmx](https://htmx.org/)
- [Alpine.js](https://alpinejs.dev/)

## Backend

- Python
- Django
- Postgres
- Redis
- Celery

# Notes

- `BusOps` has been renamed to `Workforce Planning`. References in the code will stick
  to `BusOps` for the time being, and labels will change to `Workforce Planning`.

- `HRBP` has been renamed to `HR Business Partners`. References in the code will stick
  to `HRBP` for the time being, and labels will change to `HR Business Partners`.

- `SDS status determination` has been renamed to `Status determination statement (SDS)`.
  The Django model will stay as `SDSStatusDetermination` for the time being.
