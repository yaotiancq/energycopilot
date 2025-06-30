import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate

def get_embedding_model():
    model_path = os.getenv("LOCAL_MODEL_PATH", "/app/local_model")
    return HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs={"local_files_only": True}
    )

def load_vector_db(embedding_model):
    base_dir   = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(base_dir, "faiss_index")
    db         = FAISS.load_local(
        index_path,
        embedding_model,
        allow_dangerous_deserialization=True
    )
    return db.as_retriever()

def get_prompt_template():

    prompt_template = """You are an expert in the energy industry. The following is reference information extracted from contracts or reports:
                        ---------------------
                        {context}
                        ---------------------
                        Based on the information above, answer the following question:
                        {question}
                        Please answer in as much detail as possible and base your response on the referenced content.
                      """

    return PromptTemplate(
        input_variables=["context", "question"],
        template=prompt_template
    )
