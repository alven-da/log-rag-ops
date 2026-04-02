from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import re


from vector_store import LogVectorStore

class RunbookLoader:
    def __init__(self, vectorstore):
        # This is the FAISS vectorstore from your LogVectorStore
        self.vectorstore = vectorstore
        
        # The Docstore holds the "Parent" (the full Runbook section)
        # while the Vectorstore holds the "Child" (the semantic symptoms)
        self.store = InMemoryStore()
        
        # Full sections are parents
        self.parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
        # Small chunks (like individual log templates) are children
        self.child_splitter = RecursiveCharacterTextSplitter(chunk_size=200)

        self.retriever = ParentDocumentRetriever(
            vectorstore=self.vectorstore,
            docstore=self.store,
            child_splitter=self.child_splitter,
            parent_splitter=self.parent_splitter,
        )

    def load_runbook(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read()

        # Split by H2 headers (##) to separate different incident types
        # This ensures the "Parent" is exactly one troubleshooting topic
        sections = re.split(r'\n(?=## )', content)
        
        docs = []
        for section in sections:
            if not section.strip():
                continue
            
            # Extract service name from filename or header for metadata filtering
            service_name = file_path.split('/')[-1].replace('.md', '')
            
            docs.append(Document(
                page_content=section.strip(),
                metadata={"source": file_path, "service": service_name, "type": "runbook"}
            ))

        self.retriever.add_documents(docs, ids=None)
        return self.retriever

if __name__ == "__main__":
    from log_parser import LogParser
    from vector_store import LogVectorStore # Assuming your previous class
    
    # 1. Setup Vector Store
    vs = LogVectorStore()
    
    # 2. Initialize Loader with the FAISS object
    # If vs.vector_store is None (index not created), create a blank one first
    if not vs.load_index():
        # Initialize a blank FAISS index if one doesn't exist
        from langchain_community.vectorstores import FAISS
        from langchain_community.embeddings import OllamaEmbeddings
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        # Dummy doc to init FAISS
        vs.vector_store = FAISS.from_texts(["init"], embeddings)

    loader = RunbookLoader(vs.vector_store)
    retriever = loader.load_runbook('runbook/payments.md')

    # 3. Test Retrieval with a "Log-like" query
    # Because we embed 'children', this should match the 'Symptoms' in the MD
    query = "Payment Gateway latency high"
    results = retriever.invoke(query) # Use .invoke() for modern LangChain

    for res in results:
        print(f"MATCHED RUNBOOK:\n{res.page_content}\n")
