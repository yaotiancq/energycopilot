#!/bin/bash
set -e  

REGION="us-west-1"
ACCOUNT_ID="533267074904"
REPO_NAME="energycopilot-lambda"
ECR_REPO="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME"

echo "clean image..."
if docker ps -a --format '{{.Names}}' | grep -q "$REPO_NAME"; then
  docker stop "$REPO_NAME"
  docker rm "$REPO_NAME"
fi

docker rmi -f "$REPO_NAME" || true
docker image prune -f || true

echo "build image..."
docker build -t "$REPO_NAME" .

echo "tag image..."
docker tag "$REPO_NAME:latest" "$ECR_REPO:latest"

echo "login AWS ECR..."
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

echo "upload image to ECR..."
docker push "$ECR_REPO:latest"

echo "completed：$ECR_REPO"

