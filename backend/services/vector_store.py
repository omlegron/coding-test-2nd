from typing import List, Tuple
from uuid import uuid4
from langchain.schema import Document
# from langchain.vectorstores import VectorStore
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from config import settings
import os
import logging

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self):
        # TODO: Initialize vector store (ChromaDB, FAISS, etc.)
        # pass
        # self._chunks = []
        self.db_path = "./vector_store"  # Atau ambil dari settings jika perlu
        logger.info(f"📦 Vector DB path: {self.db_path}")

        # ✅ Ganti ke HuggingFace
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cuda" if settings.use_gpu else "cpu"}
        )

        self.vectorstore = Chroma(
            persist_directory=self.db_path,
            embedding_function=self.embedding_model
        )
        logger.info("✅ VectorStore initialized")

        # if os.path.exists(self.db_path):
        #     logger.info(f"📦 Loading existing vector store from {self.db_path}")
        #     self.vectorstore = Chroma(persist_directory=self.db_path, embedding_function=self.embedding_model)
        # else:
        #     logger.info(f"🆕 Initializing new vector store at {self.db_path}")
        #     self.vectorstore = Chroma(persist_directory=self.db_path, embedding_function=self.embedding_model)
        #     self.vectorstore.persist()
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store"""
        # TODO: Implement document addition to vector store
        # - Generate embeddings for documents
        # - Store documents with embeddings in vector database
        # pass
        logger.info(f"➕ Adding {len(documents)} documents to vectorstore...")
        # self._chunks.extend(documents)
        self.vectorstore.add_documents(documents)
        self.vectorstore.persist()
        logger.info("✅ Documents added and vectorstore persisted.")
    
    def similarity_search(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Search for similar documents"""
        # TODO: Implement similarity search
        # - Generate embedding for query
        # - Search for similar documents in vector store
        # - Return documents with similarity scores
        # pass
        logger.info(f"🔍 Performing similarity search for: {query}")
        return self.vectorstore.similarity_search_with_score(query, k=k)
        # return self.chroma.similarity_search(query, k=k)

    def delete_documents(self, document_ids: List[str]) -> None:
        """Delete documents from vector store"""
        # TODO: Implement document deletion
        # pass
        try:
            logger.info(f"🗑 Deleting documents with Id: {document_ids}")
            self.vectorstore._collection.delete(ids=document_ids)
            self.vectorstore.persist()
            logger.info("✅ Document(s) deleted by Id.")
        except Exception as e:
            logger.exception(f"❌ Failed to delete by Id: {e}")
            raise e

    
    def get_document_count(self) -> int:
        """Get total number of documents in vector store"""
        # TODO: Return document count
        # pass 
        return self.vectorstore._collection.count()
    