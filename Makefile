build-recreate:
	docker-compose up --force-recreate --remove-orphans --build -d
	docker-compose run web python manage.py collectstatic --noinput
	docker-compose run web python manage.py migrate

build:
	docker-compose up --remove-orphans --build -d
	docker-compose run web python manage.py collectstatic --noinput
	docker-compose run web python manage.py migrate

build-deployment-image:
	./docker_manage.sh build

run-deployment-image:
	./docker_manage.sh run

deploy-image-aws: build-deployment-image
	./docker_manage.sh push
	./ecs_service_setup.sh

test:
	docker-compose run web env DEPLOYMENT="test" python manage.py test

log:
	docker-compose logs
