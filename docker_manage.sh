#!/bin/bash

# define AWSID and REGION in .env
source .env

case "$1" in
    build)
        docker build . -t $AWSID.dkr.ecr.$REGION.amazonaws.com/camelot:latest
        ;;
    push)
        aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin $AWSID.dkr.ecr.$REGION.amazonaws.com
        docker push $AWSID.dkr.ecr.$REGION.amazonaws.com/camelot:latest
        ;;
    run)
        docker run -p 8000:8000 $AWSID.dkr.ecr.$REGION.amazonaws.com/camelot:latest gunicorn -b 0.0.0.0:8000 projectcamelot.wsgi:application
        ;;
    *)
        echo "Please provide argument from build push run"
esac
