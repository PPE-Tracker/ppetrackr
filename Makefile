.PHONY=makemigrations migrate shell backup run

run:
	python3 manage.py runserver 0:8000

makemigrations:
	python3 manage.py makemigrations

migrate:
	python3 manage.py migrate

resetmigrations:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc"  -delete
