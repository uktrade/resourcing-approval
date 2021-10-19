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

1. `make migrate`
2. `make up`
3. `make superuser`
4. Goto http://localhost:8000/admin and login
5. Goto http://localhost:8000

# Deployment

- If you have made any changes to the dependencies, compile the new `requirements.txt`
  file using `make requirements`.

# Integrations

- GOV.UK Notify

# Test data

`John Smith : Cu{>A-pVj@MY*0C?`
