#!/bin/bash

# define AWSID and REGION
source .env_aws

case "$1" in
    build)
        docker build -f ./Dockerfile.deploy -t $AWSID.dkr.ecr.$REGION.amazonaws.com/camelot:latest
        ;;
    push)
        aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $AWSID.dkr.ecr.$REGION.amazonaws.com
        docker push $AWSID.dkr.ecr.$REGION.amazonaws.com/camelot:latest
        ;;
    run)
        docker run -p 8000:8000 $AWSID.dkr.ecr.$REGION.amazonaws.com/camelot:latest gunicorn -b 0.0.0.0:8000 projectcamelot.wsgi:application
        ;;
    *)
        echo "Please provide argument from build push run"
esac
