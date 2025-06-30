import os
import pickle
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

docs_dir = "docs" 
output_index_dir = "../faiss_index"
os.makedirs(output_index_dir, exist_ok=True)

documents = []
for filename in os.listdir(docs_dir):
    if filename.endswith(".txt"):
        with open(os.path.join(docs_dir, filename), "r", encoding="utf-8") as f:
            text = f.read()
            documents.append(Document(page_content=text, metadata={"source": filename}))

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
splits = splitter.split_documents(documents)

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
faiss_index = FAISS.from_documents(splits, embedding_model)
faiss_index.save_local(output_index_dir)

with open(os.path.join(output_index_dir, "splits.pkl"), "wb") as f:
    pickle.dump(splits, f)

print(f"FAISS vector database buit and save to : {output_index_dir}")

