# ⚡️ EnergyCopilot

**EnergyCopilot** is a real-time, serverless AI assistant that answers energy-related questions using a Retrieval-Augmented Generation (RAG) architecture with streaming token output. It integrates WebSocket management (via a lightweight ZIP-based Lambda) with scalable inference (via a containerized RAG pipeline), enabling fast, contextual Q&A grounded in source documents.

---

##  Features

-  **RAG-based GPT answering** with local FAISS + HuggingFace embeddings
-  **WebSocket streaming** via API Gateway + ZIP Lambda
-  **Asynchronous task queue** using SQS
-  **WebSocket connection tracking** using DynamoDB
-  **Semantic caching** with Qdrant (deployed on EC2)
-  **Clean UI** using React + Tailwind, with Markdown rendering
-  **Fully serverless backend**, frontend hosted on **S3 + CloudFront**

## How This Application Uses AWS Lambda
This project uses two separate AWS Lambda functions, each with a distinct responsibility and deployment method:

### 1. WebSocket Handler (ZIP-based Lambda)
Purpose: Handles WebSocket events triggered by API Gateway ($connect, $disconnect, message)  
Deployment: Packaged as a lightweight ZIP archive  

Responsibilities:
- On $connect: Stores the connectionId in DynamoDB
- On $disconnect: Removes the connectionId from DynamoDB
- On message: Extracts the user query and sends it to an SQS queue for processing
- Connected Services: API Gateway WebSocket API, DynamoDB, SQS

This Lambda is lightweight and optimized for routing and state management, ensuring fast response to connection events without blocking.

### 2. Inference Service (Container-based Lambda)
Purpose: Performs actual model inference and streams responses back to the client  
Deployment: Packaged as a Docker container and hosted in AWS Lambda  

Responsibilities:
- Triggered by SQS events (pushed by the WebSocket handler)
- Loads local FAISS index and embedding model
- Performs retrieval-augmented generation (RAG) using LangChain + OpenAI/GPT
- Streams the response token-by-token via ApiGatewayManagementApi back to the correct connectionId
- Connected Services: SQS, EC2-hosted Qdrant, API Gateway (WebSocket), ECR (for container image)

This Lambda is deployed as a container to support local models, file-based vector indices, and scalable architecture. It’s well-suited for lightweight model serving and retrieval-based applications.  


** AWS Services Used
- Lambda – handles WebSocket events and performs model inference (ZIP + container)
- API Gateway – enables real-time communication with the WebSocket client
- SQS – queues user questions for async processing
- DynamoDB – stores active WebSocket connection IDs
- S3 – hosts the frontend (React + Vite)
- CloudFront – serves the frontend globally with low latency
- ECR – stores the container image for the inference Lambda
- IAM – controls access between services
- CloudWatch – logs Lambda activity and aids debugging
- EventBridge – triggers scheduled warmup events to keep inference Lambda warm

---

##  Architecture
```text
                        [ React Frontend (S3) + Cloudfront ]
                                  ⇅ WebSocket
                        [ API Gateway (WebSocket) ]
                                  ⇅
                        [ WebSocketHandler (ZIP Lambda) ]  →  DynamoDB (connectionId tracking)
                                  ⇓
                        [ Question Queue (SQS) ]
                                  ⇓
 [ Event Bridge ]   →   [ RAG Inference (Container Lambda) ] ⇄  [ Qdrant Vector DB (on EC2) ] + [ FAISS Index ]   
                                  ⇅
                        [ GPT Response (streamed token-by-token via WebSocket) ]
```

##  Project Structure (Key Parts)
```text


energycopilot/
├── chat-ui/                  # Frontend React + Vite application
│   ├── src/
│   │   ├── App.tsx          # Main chat interface component
│   │   └── ...              # Other components and styles
│   └── dist/                # Production build output
│
├── websocket_lambda/         # ZIP-based Lambda for WebSocket management
│   ├── websocket_handler.py  # Handles $connect/$disconnect/message routes
│   └── build_websocket_zip.sh # Packaging script for deployment
|   └── requirements.txt      # dependency
│
├── lambda_handler.py         # Entry point for container-based inference Lambda
├── rag_stream.py             # Embedding, retrieval, and GPT streaming logic
├── rag_core.py               # Loads embedding model, FAISS index, and prompt
├── qdrant_cache.py           # Qdrant-based semantic cache (connects to EC2)
│
├── faiss_index/              # Locally generated FAISS vector index
├── embed/                    # Preprocessing script for document embeddings
│
├── Dockerfile                # Dockerfile for building container Lambda image
├── requirements.txt          # dependency
├── build_and_push.sh         # Script to build and push image to ECR

```

---

##  Deployment Guide

EnergyCopilot consists of four independently deployed components:

---
### 1. Prepare S3, SQS, dynamoDB, Event Bridge
- S3 for frontend host
- SQS for receiving websocket massage
- DynamoDB for store websocket connection status
- Event Bridge for warmup beat

### 2. Frontend (S3 + CloudFront)

The frontend is a React + Vite SPA hosted on S3 with optional CloudFront integration.

#### Build and Deploy

```bash
cd chat-ui
npm install
npm run build
aws s3 sync dist/ s3://your-s3-bucket-name/ --delete
```

- Enable static website hosting in S3
- Set index.html as the default root document
- Connect to CloudFront and configure a cache policy

### 3. WebSocket Management (ZIP-based Lambda)
Handles $connect, $disconnect, and message routes in API Gateway, and sends user messages to SQS. Stores WebSocket connection IDs in DynamoDB.  

Package the Lambda
```bash
cd websocket_lambda
./build_websocket_zip.sh
```
- Create a Lambda function (Python 3.10+)
- Upload websocket_handler.zip
- Set environment variables
- Enable role-based access to SQS and DynamoDB 

Configure WebSocket API (API Gateway)
Create a WebSocket API with the following routes, and connect to websocket lambda:
- $connect
- $disconnect
- message

Deploy and note the WebSocket URL

### 4. Inference Service (Container-based Lambda)
This Lambda is triggered by SQS, runs the RAG pipeline, and streams the GPT response token-by-token back to the client via WebSocket.  

Build and Push the Docker Image
```bash
./build_and_push.sh
```
- Create a Lambda function using the pushed ECR container image
- Configure environment variables
- Enable role-based access to SQS and Socket API Gateway

Configure Trigger
Add the same SQS queue as an event source trigger to this Lambda  

Configure Warmup event
Schedule an event on Event Bridge to keep inference service container alive  

### 5. Qdrant Vector Database (EC2)
Used as a semantic cache to store and retrieve previous question embeddings.

Deploy on EC2
```bash
docker run -d \
  -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```
- Ensure port 6333 is open in EC2 security group



