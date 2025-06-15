from typing import List, Dict, Any
from langchain.schema import Document
from services.vector_store import VectorStoreService
from config import settings
import logging, re, os, json

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

# from langchain_cohere import ChatCohere
from cohere import Client as CohereClient
from langchain.vectorstores import Chroma
from transformers import pipeline

logger = logging.getLogger(__name__)

def load_all_documents_from_json() -> list[Document]:
        METADATA_PATH = os.path.join(settings.pdf_upload_path, "documents_metadata.json")    

        with open(METADATA_PATH, "r") as f:
            metadata_list = json.load(f)
        
        if not metadata_list:
            return []

        # Asumsikan data urut berdasarkan waktu upload, ambil yang terakhir
        # return metadata_list[-1] 
    
        path = os.path.join(settings.pdf_upload_path, f"{metadata_list[-1]['filename']}.chunks.json")
        with open(path, "r") as f:
            data = json.load(f)
        return [Document(page_content=chunk["text"], metadata=chunk["metadata"]) for chunk in data]

class RAGPipeline:
    def __init__(self, vector_store: VectorStoreService, top_k: int = 10, similarity_threshold: float = 0.9):
        # TODO: Initialize RAG pipeline components
        # - Vector store service
        # - LLM client
        # - Prompt templates
        self.vector_store = vector_store
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.all_documents = load_all_documents_from_json()
        self.keywords = [
            "revenue", "total revenue", "net sales", "sales", "2025", "income", "amount",
            "operating profit", "growth", "increase", "change", "yoy", "year-over-year", "2024", "2023", "%",
            "cost of goods", "operating expenses", "cost", "cogs", "sg&a", "main expenses", "expenditure", "items",
            "cash flow", "operating cash", "financing cash", "investing cash", "net cash", "free cash flow",
            "debt ratio", "total liabilities", "equity", "leverage", "debt to equity", "financial structure"
        ]
       
        self.client = CohereClient(settings.openai_api_key)
        # self.generator = pipeline(
        #     "text2text-generation",
        #     model="google/flan-t5-base",  # ganti model ringan
        #     device=-1  #
        # )

        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "Answer the question based on the context:\n{context}\nQuestion: {question}"
                # "You are a financial analyst with access to company financial documents.\n"
                # "Use the following context to answer the question clearly and precisely.\n"
                # "You are allowed to perform simple calculations such as year-over-year growth, ratio computation, or identifying key items.\n"
                # "Only use the information from the context. Do not make up information.\n"
                # "If the answer cannot be determined from the context, respond with 'Not found'.\n\n"
                # "Context:\n{context}\n\n"
                # "Question:\n{question}\n\n"
                # "Answer:"
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
        
        # print('docs', docs)
        
        # fallback_docs = [
        #     doc for doc in self.all_documents
        #     if any(kw in doc.page_content.lower() for kw in self.keywords)
        # ]
        # return fallback_docs[:20]
        # print('fallback_docs[:20]', fallback_docs[:20])

        logger.info(f"🔍 Retrieving documents for question: {question}")
        docs = self._retrieve_documents(question)
        # print('docs', docs)
        # print('\n')
        context = self._generate_context(docs)
        # print('context', context)

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
            doc.metadata["score"] = score
            docs_with_scores.append(doc)

        keyword_filtered = [
            doc for doc in docs_with_scores
            if any(kw in doc.page_content.lower() for kw in self.keywords)
        ]

        threshold_filtered = sorted(
            [doc for doc in keyword_filtered if doc.metadata["score"] >= self.similarity_threshold],
            key=lambda d: d.metadata["score"],
            reverse=True
        )

        if threshold_filtered:
            logger.info(f"✅ {len(threshold_filtered)} documents passed keyword + threshold filter")
            return threshold_filtered

        if keyword_filtered:
            logger.warning(f"⚠️ No documents passed threshold. Returning {len(keyword_filtered)} keyword matches.")
            return keyword_filtered


        if not results:
            logger.warning("⚠️ No similarity search results. Trying keyword fallback on all documents...")
            fallback_docs = [
                doc for doc in self.all_documents
                if any(kw in doc.page_content.lower() for kw in self.keywords)
            ]
            return fallback_docs[:50]
        
        logger.warning(f"⚠️ No documents matched keywords. Returning top {len(docs_with_scores)} results.")
        return docs_with_scores
    
    def _generate_context(self, documents: List[Document]) -> str:
        """Generate context from retrieved documents"""
        # TODO: Generate context string from documents
        # pass
        # filtered_lines = set()  # Hindari duplikat

        # for doc_index, doc in enumerate(documents):
        #     print(f"\n📄 Document {doc_index}:")
        #     print(doc.page_content[:500])  # Lihat 500 karakter pertama, bisa kamu ubah

        #     for line in re.split(r'[\n\r]|(?<=\d)\s{2,}(?=\S)', doc.page_content):
        #         line_lower = line.lower()

        #         if any(kw in line_lower for kw in self.keywords):
        #             print(f"✅ MATCH keyword: {line.strip()}")
        #             filtered_lines.add(line.strip())

        #         if re.search(r'operating profit.*\d+', line_lower):
        #             print(f"📊 MATCH regex profit: {line.strip()}")
        #             filtered_lines.add(line.strip())


        # return "\n".join(list(filtered_lines)[:50])
        return "\n\n".join([doc.page_content for doc in documents])
   
    def _generate_llm_response(self, question: str, context: str, chat_history: List[Dict[str, str]] = None) -> str:
        prompt = self.prompt_template.format(context=context, question=question)
        # outputs = self.generator(prompt, max_length=512, do_sample=False)
        # if not outputs or "generated_text" not in outputs[0]:
        #     logger.error("❌ FLAN-T5 did not return a valid output.")
        #     return "Sorry, I can't answer that right now."

        # return outputs[0]["generated_text"]
        try:
            response = self.client.generate(
                model="command",
                prompt=prompt,
                temperature=0,
                max_tokens=512,
            )
            # print('response', response)
            return response.generations[0].text.strip()
        except Exception as e:
            logger.error(f"❌ Cohere call failed: {e}")
            return "Sorry, I can't answer that right now."
        