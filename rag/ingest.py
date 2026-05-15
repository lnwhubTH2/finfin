"""
รันครั้งเดียวเพื่อโหลดเอกสารเข้า ChromaDB
Usage: python -m rag.ingest
"""
import hashlib
from pathlib import Path
from rag.vectorstore import get_collection

KNOWLEDGE_DIR = Path(__file__).parent.parent / "data" / "knowledge"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start += size - overlap
    return [c for c in chunks if len(c) > 50]


def make_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def ingest():
    collection = get_collection()
    existing = set(collection.get()["ids"])
    total_added = 0

    for md_file in KNOWLEDGE_DIR.glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        source = md_file.name

        ids, docs, metas = [], [], []
        for chunk in chunks:
            doc_id = make_id(chunk)
            if doc_id not in existing:
                ids.append(doc_id)
                docs.append(chunk)
                metas.append({"source": source})

        if ids:
            collection.add(ids=ids, documents=docs, metadatas=metas)
            total_added += len(ids)
            print(f"  [{source}] เพิ่ม {len(ids)} chunks")
        else:
            print(f"  [{source}] ข้ามแล้ว (มีอยู่แล้ว)")

    print(f"\nสรุป: เพิ่มทั้งหมด {total_added} chunks เข้า ChromaDB")


if __name__ == "__main__":
    print("กำลัง ingest เอกสารเข้า ChromaDB...")
    ingest()
