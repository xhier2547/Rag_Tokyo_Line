"""
สคริปต์สำหรับตรวจสอบสถิติและจำนวนข้อมูลในระบบ (Dataset & Graph Verification)
- ตรวจสอบจำนวน Transit Edges (เส้นทางรถไฟ)
- ตรวจสอบจำนวน Walking Edges (เส้นทางเดินเท้าเชื่อมสถานที่กับสถานี)
- ตรวจสอบจำนวน Text Chunks สำหรับ RAG
- ตรวจสอบจำนวน Vector Chunks ใน ChromaDB
"""
import csv
import json

# 1. ตรวจสอบข้อมูลเส้นทางรถไฟ (Transit Edges)
with open('data/processed/transit_edges.csv', mode='r', encoding='utf-8') as f:
    transit_rows = list(csv.DictReader(f))

# 2. ตรวจสอบข้อมูลระยะเดินเท้าจากสถานที่ไปยังสถานี (Walking Edges)
with open('data/processed/place_station_edges.csv', mode='r', encoding='utf-8') as f:
    walking_rows = list(csv.DictReader(f))

# 3. ตรวจสอบ Text Chunks ที่ประมวลผลสำหรับ RAG
with open('data/processed/documents_chunks.json', mode='r', encoding='utf-8') as f:
    chunks = json.load(f)

# 4. ตรวจสอบจำนวนข้อมูลใน ChromaDB Vector Database
chroma_count = None
try:
    import chromadb
    client = chromadb.PersistentClient(path='data/chroma_db')
    collection = client.get_collection('tokyo_travel')
    chroma_count = collection.count()
except Exception as e:
    chroma_count = str(e)

print(f"Railway Edges (transit_edges.csv): {len(transit_rows)}")
print(f"Walking Edges (place_station_edges.csv): {len(walking_rows)}")
print(f"Text Chunks (documents_chunks.json): {len(chunks)}")
print(f"ChromaDB Chunks Count: {chroma_count}")

# 5. ตรวจสอบ Graph Cache และแจกแจงประเภทความสัมพันธ์ (Relationship types)
try:
    with open('data/processed/graph_cache.json', mode='r', encoding='utf-8') as f:
        gdata = json.load(f)
        nodes = gdata.get("nodes", [])
        links = gdata.get("links", gdata.get("edges", []))
        print(f"Graph Cache total nodes: {len(nodes)}, total links: {len(links)}")
        # แจกแจงประเภทของเส้นเชื่อมโยง (Link Breakdown)
        link_types = {}
        for l in links:
            t = l.get("type", l.get("relation", "unknown"))
            link_types[t] = link_types.get(t, 0) + 1
        print("Link breakdown:", link_types)
except Exception as e:
    print("Graph cache check:", e)
