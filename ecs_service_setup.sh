#!/bin/bash

source .env_aws

set -x

# need AWS Session Manager dependency

# wait for deployment to complete
aws ecs wait services-stable --cluster prod --services prod-backend-web

TASK_ID=$(aws ecs list-tasks --cluster prod --service-name prod-backend-web  --query 'taskArns[0]' --output text  | awk '{split($0,a,"/"); print a[3]}')
#aws ecs update-service --cluster prod --service prod-backend-web --force-new-deployment --region "$REGION"
aws ecs execute-command --task $TASK_ID --command "python manage.py collectstatic --noinput" --interactive --cluster prod --region $REGION
aws ecs execute-command --task $TASK_ID --command "python manage.py migrate" --interactive --cluster prod --region $REGION
