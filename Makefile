run:
	poetry run python src/main.py

test:
	poetry run pytest

lint:
	poetry run flake8 .
	poetry run mypy .

fix:
	poetry run black .
	poetry run isort .
