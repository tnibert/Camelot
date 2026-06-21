# Camelot

This is a nice little photo sharing web application to manage photos and share with friends and family.
I've open sourced it and would like to give it a bit of love and uplift.

High level project goals:
- Implement some form of server federation
- Promote security, privacy, and user sovereignty of data
- Promote a positive and wholesome photo sharing experience
- Interoperate with bigger fish

## Run
### Create .env
In order to run the application, you need a .env file in the project root directory defining the following environment variables:  
- SECRET_KEY
- GOOGLE_RECAPTCHA_SECRET_KEY
- GOOGLE_RECAPTCHA_PUBLIC_KEY
- SITE_DOMAIN
- ENV_DEPLOYMENT - one of either `linux` or `aws`
  - If set to `aws` must define environment variable:
    - BUCKET - the S3 bucket to store photos in

### Run Locally Using Docker Compose (Recommended)
```
$ docker-compose up --remove-orphans -d
$ docker-compose run web python manage.py migrate
```

### Run Locally, Not In Docker Container
```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt --only-binary Pillow --only-binary psycopg2-binary
$ python manage.py migrate
$ python manage.py runserver 0:8000
```

## Run Unit Tests
### From Docker Compose
```
$ docker-compose run web env DEPLOYMENT="test" python manage.py test
```

## Deploy

### AWS Deployment

Note that AWS support is not quite production ready.  Files won't be persisted.

In order to deploy onto AWS, you need a .env_aws file in the project root directory defining variables:<br>
- REGION - the region to deploy the application in  
- AWSID - the AWS user ID which will be deploying the application

There is another repository, camelot-infrastructure (https://github.com/tnibert/camelot-infrastructure)
which contains Terraform code to deploy on AWS.  From that repository root, run:<br>
```
$ terraform init
$ terraform apply
```

Then from this repository root, run:
```
$ ./docker_manage.sh build
$ ./docker_manage.sh push
```

Then login to a shell with `./aws_backend_web_shell.sh` and run python manage.py migrate.

You may need to run aws configure first to provide your credentials, if you haven't already.

### Debian Deployment

This method is no longer actively supported.  Your mileage may vary.<br>

You will need to provide the correct DATABASE_URL in your .env.<br>
Create file deploy-debian/.env-debian as described in deploy-debian/README.

Then:
```
$ cd deploy-debian
$ ./deploydebian.sh
$ ./sslcertsetup.sh
```

## API

The application can be interacted with via an API.  
This functionality is exercised by the script at https://github.com/tnibert/project-camelot-cli.