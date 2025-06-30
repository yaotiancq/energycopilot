# ⚡️ EnergyCopilot

**EnergyCopilot** is a real-time, serverless AI assistant that answers energy-related questions using a Retrieval-Augmented Generation (RAG) architecture with streaming token output over WebSocket. It integrates WebSocket management (via a lightweight ZIP-based Lambda) with scalable inference (via a containerized RAG pipeline), enabling fast, contextual Q&A grounded in source documents.

---

## 🚀 Features

- 🧠 **RAG-based GPT answering** with local FAISS + HuggingFace embeddings
- 📡 **WebSocket streaming** via API Gateway + ZIP Lambda
- 📬 **Asynchronous task queue** using Amazon SQS
- 🔗 **WebSocket connection tracking** using DynamoDB
- 🗂 **Semantic caching** with Qdrant (deployed on EC2)
- 🧼 **Clean UI** using React + Tailwind, with Markdown rendering
- ☁️ **Fully serverless backend**, frontend hosted on **S3 + CloudFront**

---

## 🧱 Architecture

[ React Frontend (S3) ]
⇅ WebSocket
[ API Gateway (WebSocket) ]
⇅
[ WebSocketHandler (ZIP Lambda) ]
⇅ DynamoDB (connectionId tracking)
⇓
[ Question Queue (SQS) ]
⇓
[ RAG Inference (Container Lambda) ]
⇅
[ Qdrant Vector DB (on EC2) ] + [ FAISS Index ]
⇓
[ GPT Response (streamed token-by-token via WebSocket) ]

## 📁 Project Structure (Key Parts)
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
├── build_and_push.sh         # Script to build and push image to ECR

```

---

## 🚀 Deployment Guide

EnergyCopilot consists of four independently deployed components:

---

### 1️⃣ Frontend (S3 + CloudFront)

The frontend is a React + Vite SPA hosted on S3 with optional CloudFront integration.

#### Build and Deploy

```bash
cd chat-ui
npm install
npm run build
aws s3 sync dist/ s3://your-s3-bucket-name/ --delete
Notes
Enable static website hosting in S3

Set index.html as the default root document

Optionally connect to CloudFront and configure a cache policy

2️⃣ WebSocket Management (ZIP-based Lambda)
Handles $connect, $disconnect, and message routes in API Gateway, and sends user messages to SQS. Stores WebSocket connection IDs in DynamoDB.

Package the Lambda
bash
复制
编辑
cd websocket_lambda
./build_websocket_zip.sh
Deploy
Create a Lambda function (Python 3.10+)

Upload websocket_handler.zip

Set environment variables:

CONNECTION_TABLE=your-dynamodb-table-name

QUESTION_QUEUE_URL=https://sqs.us-west-1.amazonaws.com/...

Configure WebSocket API (API Gateway)
Create a WebSocket API with the following routes:

$connect → your Lambda function

$disconnect → your Lambda function

message → your Lambda function

Deploy and note the WebSocket URL

3️⃣ Inference Service (Container-based Lambda)
This Lambda is triggered by SQS, runs the RAG pipeline, and streams the GPT response token-by-token back to the client via WebSocket.

Build and Push the Docker Image
bash
复制
编辑
./build_and_push.sh
Deploy
Create a Lambda function using the pushed ECR container image

Configure environment variables:

WS_API_ENDPOINT=wss://your-websocket-api.execute-api.us-west-1.amazonaws.com/dev

QDRANT_HOST=your-ec2-ip

QDRANT_PORT=6333

LOCAL_MODEL_PATH=/app/local_model

Set timeout (≥ 30s) and memory (1024–2048 MB recommended)

Configure Trigger
Add the same SQS queue as an event source trigger to this Lambda

4️⃣ Qdrant Vector Database (EC2)
Used as a semantic cache to store and retrieve previous question embeddings.

Deploy on EC2
bash
复制
编辑
docker run -d \
  -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
Notes
Ensure port 6333 is open in your EC2 security group

Optionally restrict access to Lambda VPC only

Use a persistent volume to retain vector data across restarts


