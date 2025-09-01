#! /bin/bash

# Run flake8 on all python files
flake8 auth-service . --exclude=__init__.py

# Run mypy on all python files
mypy auth-service . --exclude=__init__.py

# Run isort on all python files
isort auth-service . --recursive 

# Run black on all python files
black auth-service . 

# Run bandit on all python files
bandit -r auth-service . --exclude=__init__.py --format=json --exit-zero > auth-service-bandit-report.json






# Run tests for auth-service
cd auth-service && pytest . --cov=auth-service --cov-report=html --cov-report=json --cov-report=xml
cd ..




# Run flake8 on all python files
flake8 session-service . --exclude=__init__.py

# Run mypy on all python files
mypy session-service . --exclude=__init__.py

# Run isort on all python files
isort session-service . --recursive 

# Run black on all python files
black session-service . 

# Run bandit on all python files
bandit -r session-service . --exclude=__init__.py --format=json --exit-zero > session-service-bandit-report.json






# Run tests for auth-service
cd session-service && pytest . --cov=session-service --cov-report=html --cov-report=json --cov-report=xml
cd ..



