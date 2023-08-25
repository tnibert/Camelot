## Camelot

This is a nice little photo sharing web application to manage photos and share with friends and family.
I've recently open sourced it.  I'd like to give it a bit of love and uplift.

High level project goals:
- Implement some form of server federation
- Promote security, privacy, and user sovereignty of data
- Promote a positive and wholesome photo sharing experience
- Interoperate with bigger fish

#### Run Locally, Not In Docker Container

In order to run the application, you need a .env file in the project root directory defining variables:<br>
$SECRET_KEY - django secret key<br>
$GOOGLE_RECAPTCHA_SECRET_KEY - as it sounds<br>
$GOOGLE_RECAPTCHA_PUBLIC_KEY - as it sounds

Then:<br>
$ pip install -r requirements.txt<br>
$ python manage.py migrate<br>
$ python manage.py runserver 0:8000

Recommend creating and sourcing a venv first.<br>
You may run docker-compose up -d to easily spin up a postgres database on port 5433.  Settings.py is configured for this port.

#### Run Locally, In Docker Container

Need same .env file as above.

$ ./docker_manage.sh build<br>
$ ./docker_manage.sh run

You will probably run into a problem connecting to the database from the Docker container locally.

#### Debian Deployment

You will need to provide the correct DATABASE_URL in your .env.<br>
Create file deploy-debian/.env-debian as described in deploy-debian/README.

Then:<br>
$ cd deploy-debian<br>
$ ./deploydebian.sh<br>
$ ./sslcertsetup.sh

May the odds be ever in your favor.

#### AWS Deployment

Note that AWS support is not quite production ready.

In order to deploy onto AWS, you need a .env_aws file in the project root directory defining variables:<br>
$REGION - the region to deploy the application in<br>
$AWSID - the AWS user ID which will be deploying the application

There is another repository, camelot-infrastructure (https://github.com/tnibert/camelot-infrastructure)
which contains Terraform code to deploy on AWS.  From that repository root, run:<br>
$ terraform init<br>
$ terraform apply

Then from this repository root, run:<br>
$ ./docker_manage.sh build<br>
$ ./docker_manage.sh push

You may need to run aws configure first.

#### API

The application can be interacted with via an API.<br>
This functionality is exercised by the script at https://github.com/tnibert/project-camelot-cli.