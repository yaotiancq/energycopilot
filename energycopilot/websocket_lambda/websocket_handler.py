import os, json, boto3

dynamodb = boto3.resource("dynamodb")
conn_table = dynamodb.Table(os.environ["CONNECTION_TABLE"])
sqs = boto3.client("sqs")
queue_url = os.environ["QUESTION_QUEUE_URL"]

def lambda_handler(event, context):
    route = event["requestContext"]["routeKey"]
    conn_id = event["requestContext"]["connectionId"]

    if route == "$connect":
        conn_table.put_item(Item={"connectionId": conn_id})
        return {"statusCode": 200}

    if route == "$disconnect":
        conn_table.delete_item(Key={"connectionId": conn_id})
        return {"statusCode": 200}

    if route == "message":
        body = json.loads(event.get("body","{}"))
        question = body.get("data","").strip()
        if not question:
            return {"statusCode": 400, "body": "Empty message"}
        
        # SQS enquere
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                "connectionId": conn_id,
                "question": question
            })
        )
        return {"statusCode": 200}

    return {"statusCode": 400, "body": "Unknown route"}

if __name__ == "__main__":
    # os.environ["CONNECTION_TABLE"] = "your-connection-table-name"
    # os.environ["QUESTION_QUEUE_URL"] = "https://sqs.us-west-1.amazonaws.com/123456789012/your-queue-name"

    #  $connect
    event_connect = {
        "requestContext": {
            "routeKey": "$connect",
            "connectionId": "test-conn-1"
        }
    }
    print(">>> $connect response:")
    print(lambda_handler(event_connect, None))

    # message
    event_message = {
        "requestContext": {
            "routeKey": "message",
            "connectionId": "test-conn-1"
        },
        "body": json.dumps({
            "data": "What is the energy policy in California?"
        })
    }
    print("\n>>> message response:")
    print(lambda_handler(event_message, None))

    #  $disconnect
    event_disconnect = {
        "requestContext": {
            "routeKey": "$disconnect",
            "connectionId": "test-conn-1"
        }
    }
    print("\n>>> $disconnect response:")
    print(lambda_handler(event_disconnect, None))

