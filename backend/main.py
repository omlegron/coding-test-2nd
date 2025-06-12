from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models.schemas import ChatRequest, ChatResponse, DocumentsResponse, UploadResponse
from services.pdf_processor import PDFProcessor
from services.vector_store import VectorStoreService
from services.rag_pipeline import RAGPipeline
from config import settings
import logging
import time
import os
import json
from datetime import datetime


# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG-based Financial Statement Q&A System",
    description="AI-powered Q&A system for financial documents using RAG",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
# TODO: Initialize your services here
pdf_processor = None
vector_store = None
rag_pipeline = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global pdf_processor, vector_store, rag_pipeline

    logger.info("🚀 Starting RAG Q&A System...")

    pdf_processor = PDFProcessor()
    vector_store = VectorStoreService()
    rag_pipeline = RAGPipeline(vector_store=vector_store)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "RAG-based Financial Statement Q&A System is running"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file"""
    start_time = time.time()


    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")


    os.makedirs(settings.pdf_upload_path, exist_ok=True)
    saved_path = os.path.join(settings.pdf_upload_path, file.filename)

    with open(saved_path, "wb") as f:
        f.write(await file.read())


    try:
        chunks = pdf_processor.process_pdf(saved_path)
    except Exception as e:
        logger.exception("❌ Error processing PDF")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


    try:
        for chunk in chunks:
            chunk.metadata["filename"] = file.filename

        vector_store.add_documents(chunks)

        # vector_store.add_documents(chunks, metadata={"filename": file.filename})
    except Exception as e:
        logger.exception("❌ Error saving to vector store")
        raise HTTPException(status_code=500, detail=f"Failed to store embeddings: {str(e)}")


    elapsed = round(time.time() - start_time, 2)
    logger.info(f"✅ Uploaded and processed: {file.filename} ({len(chunks)} chunks, {elapsed}s)")

    metadata_list = load_documents_metadata()
    metadata_list.append({
        "filename": file.filename,
        "upload_date": datetime.utcnow().isoformat() + "Z",
        "chunks_count": len(chunks),
        "status": "processed"
    })

    save_documents_metadata(metadata_list)

    store_chunks(file, chunks)

    return UploadResponse(
        filename=file.filename,
        chunks_count=len(chunks),
        processing_time=elapsed,
        message="Upload successful"
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat request and return AI response"""
    # TODO: Implement chat functionality
    # 1. Validate request
    # 2. Use RAG pipeline to generate answer
    # 3. Return response with sources
    # pass
    start_time = time.time()

    query = request.question.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # 1. Retrieve relevant documents
    relevant_docs = rag_pipeline._retrieve_documents(query)
    if not relevant_docs:
        processing_time = round(time.time() - start_time, 2)
        return ChatResponse(
            answer="Sorry, I couldn't find relevant information.",
            sources=[],
            processing_time=processing_time
        )

    # 2. Generate answer
    answer_data = rag_pipeline.generate_answer(query, relevant_docs)

    # 3. Return response
    processing_time = round(time.time() - start_time, 2)
    return ChatResponse(
        answer=answer_data['answer'],
        sources=answer_data['sources'],
        processing_time=processing_time
    )


@app.get("/api/documents")
async def get_documents():
    """Get list of processed documents"""
    # TODO: Implement document listing
    # - Return list of uploaded and processed documents
    # pass
    metadata_list = load_documents_metadata()
    return {"documents": metadata_list}


@app.get("/api/chunks")
async def get_chunks():
    """Get document chunks (optional endpoint)"""
    # TODO: Implement chunk listing
    # - Return document chunks with metadata
    # pass
    result = []
    try:
        for fname in os.listdir(settings.pdf_upload_path):
            if fname.endswith(".chunks.json"):
                with open(os.path.join(settings.pdf_upload_path, fname), "r") as f:
                    file_chunks = json.load(f)
                    result.extend(file_chunks)
        return {"chunks": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load chunks: {str(e)}")


METADATA_PATH = os.path.join(settings.pdf_upload_path, "documents_metadata.json")
def load_documents_metadata():
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r") as f:
            return json.load(f)
    return []

def save_documents_metadata(metadata_list):
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata_list, f, indent=2)

def store_chunks(file, chunks):
    chunk_json_path = os.path.join(settings.pdf_upload_path, f"{file.filename}.chunks.json")
    with open(chunk_json_path, "w") as f:
        json.dump([
            {"text": c.page_content, "metadata": c.metadata}
            for c in chunks
        ], f, indent=2)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug) 

