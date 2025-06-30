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
├── chat-ui/ # React + Tailwind frontend
├── websocket_lambda/ # ZIP Lambda for WebSocket control and SQS enqueue
│ ├── websocket_handler.py
│ ├── build_websocket_zip.sh
│ └── websocket_handler.zip
│
├── Dockerfile # Container Lambda (RAG inference)
├── lambda_handler.py # Unified handler for SQS and HTTP
├── stream_answer.py # Core logic for streaming GPT response
├── rag_core.py # Load embedding model, FAISS, prompt
├── qdrant_cache.py # Qdrant-based semantic cache (connects to EC2)
├── embed/ # One-time document embedder
├── faiss_index/ # FAISS index and associated metadata
text

---

## ⚙️ Deployment

### 1. WebSocket Management Lambda (ZIP-based)

Handles `$connect`, `$disconnect`, and incoming message routing. Stores connectionId in DynamoDB and pushes user messages to SQS.

```bash
cd websocket_lambda
./build_websocket_zip.sh
# Upload websocket_handler.zip to Lambda and connect via API Gateway WebSocket routes



