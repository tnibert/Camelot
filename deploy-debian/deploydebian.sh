#!/usr/bin/env bash

# based on https://djangocentral.com/deploy-django-with-nginx-gunicorn-postgresql-and-lets-encrypt-ssl-on-ubuntu/

set -e
set -x

# defines $USER, $PASSWORD, $DOMAIN
# use same $USER as both postgres and linux username
source .env_debian

sudo apt-get install postgresql postgresql-contrib libpq-dev python3-dev nginx

sudo -u postgres psql << EOF
CREATE DATABASE camelot;
CREATE USER $USER WITH ENCRYPTED PASSWORD $PASSWORD;
ALTER ROLE $USER SET client_encoding TO 'utf8';
ALTER ROLE $USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE camelot TO $USER;
\q
EOF

sudo apt install python3-venv

python3 -m venv camelotvenv
source camelotvenv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# if the argument restore has been passed to the script, we will load in a database backup bak.dump
if [ "$1" = "restore" ]; then
  pg_restore --create -U $USER -d camelot -v --single-transaction bak.dump
else
  python manage.py migrate
fi

python manage.py check --deploy

sudo mkdir /var/gunicorn
sudo chown $USER /var/gunicorn

cat > gunicorn.service << EOF
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/home/$USER/camelot
ExecStart=/home/$USER/camelot/camelotvenv/bin/gunicorn --access-logfile - --workers 15 --bind unix:/var/gunicorn/camelot.sock projectcamelot.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo mv gunicorn.service /etc/systemd/system/

sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn

# to reload config after service file change:
# sudo systemctl daemon-reload
# sudo systemctl restart gunicorn

# set static root? then -
#python manage.py collectstatic

cat > camelot << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location = /favicon.ico { access_log off; log_not_found off; }
    location  /static/ {
        root /home/$USER/camelot/camelot;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/gunicorn/camelot.sock;
    }
}
EOF
sudo mv camelot /etc/nginx/sites-available/

sudo ln -s /etc/nginx/sites-available/camelot /etc/nginx/sites-enabled

sudo nginx -t
sudo systemctl restart nginx

# allow nginx in firewall
sudo ufw allow 'Nginx Full'