import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document

class LogVectorStore:
    def __init__(self, index_path="data/faiss_index"):
        self.index_path = index_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.vector_store = None

    def get_index(self):
        """Returns the current FAISS instance, loading it if necessary."""
        if self.vector_store is not None:
            return self.vector_store
        
        if not self.load_index():
            # If no index exists, we initialize a blank one with a placeholder
            # FAISS requires at least one document to initialize
            print("Creating new empty FAISS index...")
            init_doc = Document(page_content="init", metadata={"type": "system"})
            self.vector_store = FAISS.from_documents([init_doc], self.embeddings)
            
        return self.vector_store

    def create_and_save(self, processed_docs):
        """Standard batch ingestion for logs."""
        documents = [
            Document(page_content=d["page_content"], metadata=d["metadata"]) 
            for d in processed_docs
        ]

        print("🔄 Generating embeddings via Ollama...")
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        self.save()
        print(f"✅ FAISS index saved to {self.index_path}")

    def load_index(self):
        # FAISS saves a folder containing index.faiss and index.pkl
        if os.path.exists(os.path.join(self.index_path, "data/faiss_index/index.faiss")):
            self.vector_store = FAISS.load_local(
                self.index_path, 
                self.embeddings, 
                allow_dangerous_deserialization=True 
            )
            return True
        return False

    def save(self):
        """Persist current state to disk."""
        if self.vector_store:
            self.vector_store.save_local(self.index_path)

    def search(self, query: str, k=5):
        index = self.get_index()
        return index.similarity_search(query, k=k)
    
if __name__ == "__main__":
    from log_parser import LogParser
    
    # 1. Parse
    parser = LogParser()
    docs = parser.parse_file('data/raw_logs/logs.json')
    
    # 2. Store
    vs = LogVectorStore()
    vs.create_and_save(docs)
    
    # 3. Test Query
    # results = vs.search("Show me database connection timeouts")
    # results = vs.search("Show me cache hit logs")
    results = vs.search("Session related errors")

    for res in results:
        print(f"[{res.metadata['level']}] {res.page_content}")