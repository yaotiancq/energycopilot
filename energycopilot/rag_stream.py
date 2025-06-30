import json
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from qdrant_cache import search_cache, add_to_cache
from rag_core import get_embedding_model, load_vector_db, get_prompt_template

class WebSocketStreamer(BaseCallbackHandler):
    def __init__(self, ws_client, connection_id):
        self.ws = ws_client
        self.conn_id = connection_id
        self.collected_tokens = []

    def on_llm_new_token(self, token: str, **kwargs):
        self.collected_tokens.append(token)
        self.ws.post_to_connection(
            ConnectionId=self.conn_id,
            Data=json.dumps({"response": token})
        )

def stream_answer(question, connection_id, ws_client):
    #  cache hit
    cached = search_cache(question)
    if cached:
        ws_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps({"response": cached, "done": True})
        )
        return

    # cache miss
    embedding_model = get_embedding_model()
    retriever = load_vector_db(embedding_model)

    # Prompt template
    prompt = get_prompt_template()

    # LLM
    streamer = WebSocketStreamer(ws_client, connection_id)
    llm = ChatOpenAI(
        model="gpt-4.1-nano", 
        temperature=0,
        streaming=True,
        callback_manager=CallbackManager([streamer])
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )

    result = qa_chain.invoke({"query": question})

    # response
    ws_client.post_to_connection(
        ConnectionId=connection_id,
        Data=json.dumps({"response": "", "done": True})
    )
    add_to_cache(question, result["result"])

if __name__ == "__main__":

    import os
    os.environ["LOCAL_MODEL_PATH"] = "./local_model"

    # WebSocket client simulation
    class MockWebSocketClient:
        def __init__(self):
            self.buffer = []

        def post_to_connection(self, ConnectionId, Data):
            print(f"[{ConnectionId}] --> {Data}")
            self.buffer.append((ConnectionId, json.loads(Data)))

    question = "What is the purpose of a power purchase agreement?"
    conn_id = "test-connection-001"
    mock_ws = MockWebSocketClient()

    stream_answer(question, conn_id, mock_ws)

    print("\n Full response:")
    for _, msg in mock_ws.buffer:
        if msg["response"]:
            print(msg["response"], end="", flush=True)
    print("\n Done.")