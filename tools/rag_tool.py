from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import os

class RAGTool:
    _instance = None
    _vectorstore = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._vectorstore is None:
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self._build_vectorstore()

    def _build_vectorstore(self):
        print("[RAGTool] Building vector store...")
        documents = []
        for filename in os.listdir("knowledge_base"):
            if filename.endswith(".txt"):
                loader = TextLoader(
                    os.path.join("knowledge_base", filename),
                    encoding="utf-8"
                )
                documents.extend(loader.load())
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)
        RAGTool._vectorstore = FAISS.from_documents(chunks, self.embeddings)
        print("[RAGTool] Vector store ready!")

    def retrieve(self, query: str, k: int = 3) -> str:
        docs = RAGTool._vectorstore.similarity_search(query, k=k)
        return "\n\n".join([doc.page_content for doc in docs])
