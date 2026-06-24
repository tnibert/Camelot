build-recreate:
	docker-compose up --force-recreate --remove-orphans --build -d
	docker-compose run web python manage.py collectstatic --noinput

build:
	docker-compose up --remove-orphans --build -d
	docker-compose run web python manage.py collectstatic --noinput

test:
	docker-compose run web env DEPLOYMENT="test" python manage.py test

log:
	docker-compose logs
