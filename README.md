# resourcing-approval

# Local environment

## Requirements

- make
- docker
- docker-compose
- [poetry](https://python-poetry.org/docs/#installation)

## Setup

1. `cp .env.example .env`
2. `npm install`
3. `make build`

## Running

1. `make first-use`
2. Goto http://localhost:8000/admin and login
   - You can find the login details for test users on confluence
3. Goto http://localhost:8000

# Deployment

- If you have made any changes to the dependencies, compile the new `requirements.txt`
  file using `make requirements`.

# Integrations

- GOV.UK Notify

# Notes

- `BusOps` has been renamed to `Workforce Planning`. References in the code will stick
  to `BusOps` for the time being, and labels will change to `Workforce Planning`.

- `HRBP` has been renamed to `HR Business Partners`. References in the code will stick
  to `HRBP` for the time being, and labels will change to `HR Business Partners`.
