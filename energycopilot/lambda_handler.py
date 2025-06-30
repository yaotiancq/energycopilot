import json
import os
import boto3
from rag_stream import stream_answer

def lambda_handler(event, context):
    if event.get("warmup"):
        print("Warmup ping received")

    # message from SQS
    if "Records" in event and event["Records"][0].get("eventSource") == "aws:sqs":
        ws_endpoint = os.environ["WS_API_ENDPOINT"]
        ws_client = boto3.client("apigatewaymanagementapi", endpoint_url=ws_endpoint)

        for record in event["Records"]:
            try:
                body = json.loads(record["body"])
                stream_answer(
                    question=body["question"],
                    connection_id=body["connectionId"],
                    ws_client=ws_client
                )
            except Exception as e:
                print(f"Error processing record: {e}")
        return {"statusCode": 200}

    # Unknown request
    return {
        "statusCode": 400,
        "body": json.dumps({"error": "Unknown event source"}),
        "headers": {"Content-Type": "application/json"}
    }    