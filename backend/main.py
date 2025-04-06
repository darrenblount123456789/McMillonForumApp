from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Document
import boto3
import os
from dotenv import load_dotenv
import uuid
from typing import List
from pinecone import Pinecone
from openai import OpenAI
import mammoth
from io import BytesIO
from botocore.exceptions import NoCredentialsError
from fastapi.middleware.cors import CORSMiddleware
from botocore.config import Config




# Load environment variables
load_dotenv()

# Initialize Pinecone & OpenAI
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# AWS S3 Configuration
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION")
S3_CLIENT = boto3.client(
    "s3",
    region_name=S3_REGION, 
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    config=Config(signature_version='s3v4'),
)


def generate_presigned_url(s3_file_name, original_file_name, expiration=3600):
    """Generate a pre-signed URL that forces downloads with the original filename."""
    try:
        presigned_url = S3_CLIENT.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": S3_BUCKET,
                "Key": f"documents/{s3_file_name}",
                "ResponseContentDisposition": f'attachment; filename="{original_file_name}"'  
            },
            ExpiresIn=expiration
        )
        # print(f"✅ Generated presigned URL: {presigned_url}")  # Debugging
        return presigned_url
    except Exception as e:
        print(f"❌ Error generating presigned URL: {e}")
        return None





# Initialize FastAPI
app = FastAPI()

# Allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

async def extract_text_from_file(file_content: bytes) -> str:
    """Extracts text from .docx or .txt files."""
    # print(f"Extracting text... File size: {len(file_content)} bytes")

    if len(file_content) == 0:
        print("🚨 File content is empty!")
        return ""

    if file_content[:4] != b"PK\x03\x04":  # DOCX files are ZIP archives
        print(" Not a valid DOCX file (missing ZIP signature)")
        return ""

    try:
        text = mammoth.extract_raw_text(BytesIO(file_content)).value
    except Exception as e:
        print(f"❌ Error processing DOCX file: {e}")
        text = ""

    return text


def generate_embedding(text: str):
    """Generate embedding vector using OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Upload file to S3, extract text, generate embeddings, and store metadata in PostgreSQL & Pinecone."""
    
    # Read file content into memory
    file_content = await file.read()
    # print(f" File received: {file.filename}, Size: {len(file_content)} bytes")

    # Extract text
    extracted_text = await extract_text_from_file(file_content)
    # print(f"Extracted Text: {extracted_text[:500]}")  # Print first 500 chars

    # Generate unique filename for S3 (UUID)
    file_ext = file.filename.split(".")[-1]  # Extract file extension
    s3_file_name = f"{uuid.uuid4()}.{file_ext}"  # UUID filename
    s3_path = f"documents/{s3_file_name}"

    # Upload file to S3
    S3_CLIENT.upload_fileobj(BytesIO(file_content), S3_BUCKET, s3_path)

    # Generate embedding if text exists
    embedding = generate_embedding(extracted_text) if extracted_text else None

    # Store metadata in PostgreSQL
    new_document = Document(
        file_name=file.filename,  # Original filename for display
        s3_file_name=s3_file_name,  # UUID filename for S3 storage
        file_type=file.content_type,
        file_path=f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_path}",  # S3 URL
        text_content=extracted_text
    )
    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)

    # Store embedding in Pinecone
    if embedding:
        index.upsert([
            (
                str(new_document.id),
                embedding,
                {
                    "file_name": new_document.file_name,  #  Originl name
                    "s3_file_name": new_document.s3_file_name,  #  UUID filename
                    "file_url": new_document.file_path  #  S3 URL
                }
            )
        ])
        # print(" Embedding stored in Pinecone")

    return {
        "message": "File uploaded successfully!",
        "file_url": new_document.file_path,
        "original_name": new_document.file_name  #  Send original name to frontend
    }


@app.get("/search/")
async def search_documents(query: str, db: AsyncSession = Depends(get_db)):
    """Search documents using Pinecone vector similarity and generate AI responses with extracted text from PostgreSQL."""
    
    # Step 1: Generate embedding for the query
    query_embedding = generate_embedding(query)

    # Step 2: Query Pinecone for relevant documents
    search_results = index.query(vector=query_embedding, top_k=5, include_metadata=True)

    # Step 3: Retrieve matching documents' metadata and extract IDs
    matched_docs = [
        {
            "id": match["id"],
            "score": match["score"],
            "file_name": match["metadata"]["file_name"],
            "s3_file_name": match["metadata"]["s3_file_name"],
            "file_url": generate_presigned_url(match["metadata"]["s3_file_name"], match["metadata"]["file_name"]),
        }
        for match in search_results["matches"] if match["score"] >= 0.5  
    ]

    if not matched_docs:
        return {"query": query, "response": "No relevant documents found.", "results": []}

    # Step 4: Retrieve extracted text from PostgreSQL based on document IDs
    doc_ids = [int(doc["id"]) for doc in matched_docs]
    result = await db.execute(select(Document).filter(Document.id.in_(doc_ids)))
    documents = result.scalars().all()

    # Step 5: Use OpenAI to generate a human-like response based on document text
    document_texts = "\n\n".join([doc.text_content for doc in documents if doc.text_content])

    ai_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant that provides concise, helpful responses based on documents."},
            {"role": "user", "content": f"Based on the following documents, answer the query: '{query}'\n\n{document_texts}"}
        ]
    )

    response_text = ai_response.choices[0].message.content

    return {
        "query": query,
        "response": response_text,
        "results": matched_docs
    }





@app.get("/files/", response_model=List[dict])
async def list_files(db: AsyncSession = Depends(get_db)):
    """Retrieve a list of uploaded files and generate signed URLs with correct download names."""
    result = await db.execute(select(Document))
    files = result.scalars().all()

    if not files:
        return []

    file_list = []
    for file in files:
        presigned_url = generate_presigned_url(file.s3_file_name, file.file_name)  #  Pass both names
        # print(f"📢 Generating presigned URL for {file.file_name}: {presigned_url}")  # Debugging

        file_list.append({
            "id": file.id,
            "file_name": file.file_name,  #  Display original name in React
            "file_url": presigned_url,  #  URL now forces correct download name
            "uploaded_at": file.uploaded_at,
        })

    return file_list

