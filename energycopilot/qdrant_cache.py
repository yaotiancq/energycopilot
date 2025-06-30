import os
import uuid
import re
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client.models import Filter

QDRANT_HOST = os.getenv("QDRANT_HOST", "your-ec2-ip")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "semantic_cache"
EMBEDDING_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "/app/local_model")

IS_LOCAL = __name__ == "__main__"
if IS_LOCAL:
    mbedding_model = HuggingFaceEmbeddings(model_name="./local_model", model_kwargs={"local_files_only": True})
else:
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_PATH, model_kwargs={"local_files_only": True})

scores=[]

# Qdrant 
def get_client():
    try:
        return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=2.0)
    except Exception as e:
        print(f"[warn] Qdrant client init failed: {e}")
        return None

def clean_text(text: str) -> str:
    # text = text.strip()
    # # text = text.lower()                    
    # text = re.sub(r"\s+", " ", text)           
    # text = re.sub(r"[?!.]$", "", text)         
    return text

# add to cache when no hit
def add_to_cache(question: str, answer: str):
    try:
        client = get_client()
        if not client:
            return
        
        clean_question = clean_text(question)
        vector = embedding_model.embed_query(clean_question)
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={"question": question, "answer": answer}
                )
            ]
        )
    except Exception as e:
        print(f"[warn] Qdrant add_to_cache failed: {e}")

# search cache
def search_cache(query: str, threshold=0.65):
    try:
        client = get_client()
        if not client:
            return None

        clean_query = clean_text(query)
        embed_vector = embedding_model.embed_query(clean_query)
        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=embed_vector,     
            limit=1,
            with_payload=True
        )

        hits = response.points
        if not hits:
            return None

        top = hits[0]
        # debug
        print(f"[debug] top.score = {top.score}, question = {top.payload['question']}")

        scores.append(top.score)

        if top.score > threshold:
            return top.payload["answer"]

    except Exception as e:
        print(f"[warn] Qdrant search_cache failed: {e}")
    return None


# module test
if __name__ == "__main__":
    flag=True  # True: delete all data, False: continue
    client = get_client()
    if flag:
        client.delete(collection_name=COLLECTION_NAME, points_selector=Filter(must=[]))
    else:
        if client:
            
            if not client.collection_exists(COLLECTION_NAME):
                client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )

            print(f"[init] Collection '{COLLECTION_NAME}' is ready.")

            count = client.count(collection_name=COLLECTION_NAME, exact=True)

            print("count: ", count)

        q1 = "What is the duration of the contract?"
        a1 = "The contract is valid for 3 years starting from January 2024."
        add_to_cache(q1, a1)

        q_test = "How long does the agreement last?"
        q_test = "What is the duration of the contract?"
        q_tests = ["How long does the contract last?",
                    "What is the length of the agreement?",
                    "For how many years is the contract valid?",
                    "What’s the term of the contract?",
                    "How long will the agreement remain in effect?",
                    "What is the validity period of the contract?",
                    "Until when is the contract effective?",
                    "What’s the expiration date of the agreement?",
                    "What is the contract’s duration?",
                    "Over what time frame does the contract apply?",
                    "How long is the contract in force?",
                    "What time period does the agreement cover?",
                    "Is the contract valid for a specific number of years?",
                    "When does the contract start and end?",
                    "What is the total contractual period?",
                    "How many months or years does the agreement last?",
                    "When does the agreement expire?",
                    "What is the effective period of the contract?",
                    "Does the contract have a fixed term?",
                    "Is this a long-term or short-term contract?"]
        for q_test in q_tests:
            result = search_cache(q_test)
            if result:
                print(f"[cache hit] {result}")
            else:
                print("[cache miss]")
            
            print('\n')

        print("average score: ", sum(scores)/len(scores))
