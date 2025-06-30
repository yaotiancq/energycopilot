# ✅ AWS  Python 3.10
FROM public.ecr.aws/lambda/python:3.10

# ✅ swig
RUN yum install -y swig

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY lambda_handler.py .
COPY faiss_index/ ./faiss_index/
COPY qdrant_cache.py .
COPY rag_core.py .
COPY rag_stream.py .

COPY local_model/ /app/local_model/

ENV HF_HOME=/tmp
ENV TRANSFORMERS_CACHE=/tmp

CMD ["lambda_handler.lambda_handler"]