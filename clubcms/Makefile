.PHONY: build up down logs shell migrate test superuser collectstatic demo

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f web

shell:
	docker compose exec web python manage.py shell

migrate:
	docker compose exec web python manage.py migrate

test:
	docker compose exec web pytest

superuser:
	docker compose exec web python manage.py createsuperuser

collectstatic:
	docker compose exec web python manage.py collectstatic --noinput

demo:
	docker compose exec web python manage.py build_demo_db
	docker compose exec web python manage.py load_demo --lang en --primary --flush
	docker compose exec web python manage.py load_demo --lang it
	docker compose exec web python manage.py collectstatic --noinput

makemessages:
	docker compose exec web python manage.py makemessages -l it -l en -l de -l fr -l es

compilemessages:
	docker compose exec web python manage.py compilemessages
