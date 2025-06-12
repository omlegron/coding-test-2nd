from typing import List, Dict, Any
from langchain.schema import Document
from services.vector_store import VectorStoreService
from config import settings
import logging

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from transformers import pipeline

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self, vector_store: VectorStoreService, top_k: int = 10, similarity_threshold: float = 0.7):
        # TODO: Initialize RAG pipeline components
        # - Vector store service
        # - LLM client
        # - Prompt templates
        self.vector_store = vector_store
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        
        self.generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-base",  # ganti model ringan
            device=-1  #
        )

        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are a financial analyst.\n"
                "Use the following context to answer the question clearly and accurately.\n\n"
                "Context:\n{context}\n\n"
                "Question:\n{question}\n\n"
                "Answer:"
            )
        )

    def generate_answer(self, question: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate answer using RAG pipeline"""
        # TODO: Implement RAG pipeline
        # 1. Retrieve relevant documents
        # 2. Generate context from retrieved documents
        # 3. Generate answer using LLM
        # 4. Return answer with sources
        # pass
        logger.info(f"🔍 Retrieving documents for question: {question}")
        docs = self._retrieve_documents(question)
        context = self._generate_context(docs)
        logger.info(f"🧠 Generating answer using HF model")
        answer = self._generate_llm_response(question, context, chat_history)
        
        sources = [
            {
                "content": doc.page_content[:200],
                "page": doc.metadata.get("page", 0),
                "score": doc.metadata.get("score", 0.0),
                "metadata": doc.metadata
            }
            for doc in docs
        ]

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_docs_count": len(docs)
        }
    
    def _retrieve_documents(self, query: str) -> List[Document]:
        """Retrieve relevant documents for the query"""
        # TODO: Implement document retrieval
        # - Search vector store for similar documents
        # - Filter by similarity threshold
        # - Return top-k documents
        # pass
        results = self.vector_store.similarity_search(query, k=self.top_k)
        docs_with_scores = []

        for doc, score in results:
            logger.debug(f"📄 Doc score: {score:.4f} | Page: {doc.metadata.get('page')}")
            doc.metadata["score"] = score  # 🟢 Simpan skor di metadata
            docs_with_scores.append(doc)

        filtered_docs = [doc for doc in docs_with_scores if doc.metadata["score"] >= self.similarity_threshold]

        if not filtered_docs:
            logger.warning("⚠️ No documents passed similarity threshold, returning top results anyway")
            filtered_docs = docs_with_scores

        logger.info(f"📄 Retrieved {len(filtered_docs)} relevant documents.")
        return filtered_docs
    
    def _generate_context(self, documents: List[Document]) -> str:
        """Generate context from retrieved documents"""
        # TODO: Generate context string from documents
        # pass
        return "\n\n".join([doc.page_content for doc in documents])
    
    def _generate_llm_response(self, question: str, context: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Generate response using LLM"""
        # TODO: Implement LLM response generation
        # - Create prompt with question and context
        # - Call LLM API
        # - Return generated response
        # pass 
        prompt = self.prompt_template.format(context=context, question=question)

        outputs = self.generator(prompt, max_length=512, do_sample=False)
        if not outputs or "generated_text" not in outputs[0]:
            logger.error("❌ FLAN-T5 did not return a valid output.")
            return "Sorry, I can't answer that right now."

        return outputs[0]["generated_text"]
