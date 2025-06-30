docker stop local-lambda && docker rm local-lambda

docker run -d -p 9000:8080 --name local-lambda \
  --env-file .env \
  -v "$PWD/aws-lambda-rie:/usr/local/bin/aws-lambda-rie" \
 energycopilot-lambda 

  
curl -s -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{
  "Records": [
    {
      "eventSource": "aws:sqs",
      "body": "{\"question\": \"What is net metering?\", \"connectionId\": \"test-conn-id-001\"}"
    }
  ]
  }'
