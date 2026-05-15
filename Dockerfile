FROM python:3.12-slim

WORKDIR /app

# ติดตั้ง dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy โค้ดทั้งหมด
COPY . .

# Ingest knowledge base
RUN python rag/ingest.py

EXPOSE 7860

CMD ["python", "app.py"]