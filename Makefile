run:
	poetry run python -m case.main

lint:
	poetry run flake8 case

test:
	poetry run pytest

code-coverage:
	poetry run pytest --cov
