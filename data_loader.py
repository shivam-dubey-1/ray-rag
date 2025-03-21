# load_qdrant.py
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import json
from tqdm import tqdm
import time

def load_jsonl(file_path):
    """Load data from JSONL file"""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():  # Skip empty lines
                data.append(json.loads(line))
    return data

def main():
    # Initialize Qdrant client
    client = QdrantClient("localhost", port=6333)  # Assuming port-forward is set up
    
    # Initialize the embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Load data
    print("Loading data from JSONL...")
    data = load_jsonl("/home/ubuntu/environment/gpu-workshop/rag/v2/data.jsonl")
    print(f"Loaded {len(data)} records")
    
    # Create collection
    print("Creating collection...")
    client.recreate_collection(
        collection_name="knowledge_base",
        vectors_config={
            "size": 384,  # Size of the embedding vector
            "distance": "Cosine"
        }
    )
    
    # Process and upload data in batches
    batch_size = 100
    total_processed = 0
    
    print("Processing and uploading data...")
    for i in tqdm(range(0, len(data), batch_size)):
        batch = data[i:i + batch_size]
        
        # Create embeddings for the batch
        vectors = []
        for item in batch:
            if "text" not in item:
                print(f"Skipping item without text field: {item}")
                continue
                
            embedding = model.encode(item["text"])
            vector = {
                "id": abs(hash(f"{item['text']}_{time.time()}")),
                "vector": embedding.tolist(),
                "payload": item
            }
            vectors.append(vector)
        
        # Upload vectors to Qdrant
        if vectors:
            client.upsert(
                collection_name="knowledge_base",
                points=vectors
            )
            total_processed += len(vectors)
    
    print(f"\nProcessing complete! Total records processed: {total_processed}")
    
    # Verify the upload
    collection_info = client.get_collection("knowledge_base")
    print("\nCollection Info:")
    print(f"Points count: {collection_info.points_count}")
    print(f"Vectors count: {collection_info.vectors_count}")

if __name__ == "__main__":
    main()
