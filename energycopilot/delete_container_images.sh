#!/bin/bash
docker stop local-lambda && docker rm local-lambda
docker rmi energycopilot-lambda:latest
docker rmi 533267074904.dkr.ecr.us-west-1.amazonaws.com/energycopilot-lambda:latest

docker ps -a
docker images
