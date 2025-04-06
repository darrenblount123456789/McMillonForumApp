# Forum Application

This project is a full-stack Forum Application designed for companies to create a centralized space where teams can upload .docx documents and make all internal data easily searchable.
It helps reduce the problem of tribal knowledge by ensuring that important information is accessible across teams.
Users can upload files, view and download documents, and submit human-language queries like "I want to know about the policy on smoking", and the system will generate AI-based responses with the most relevant documents.

## Technologies Used

- **React + Vite** (Frontend)
- **FastAPI** (Backend)
- **PostgreSQL** (Metadata Storage)
- **AWS S3** (File Storage)
- **Pinecone** (Vector Storage)
- **OpenAI API** (Embedding + Chat Completions)

---

## How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/forum-application.git
cd forum-application
```

> _Note: Replace `yourusername` with your GitHub username._

---

### 2. Setup Environment Variables

Create a `.env` file inside the `backend/` directory with the following:

```env
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
S3_BUCKET_NAME=your_s3_bucket_name
S3_REGION=your_s3_region
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=your_pinecone_index_name
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost/forum_db
```

---

### 3. Start the PostgreSQL Database

Make sure PostgreSQL is running locally and the `forum_db` database exists.  
You can connect like this:

```bash
psql -U postgres -d forum_db
```

---

### 4. Start the Backend (FastAPI)

Navigate to the backend folder:

```bash
cd backend
uvicorn main:app --reload
```

The backend will start at:

```
http://127.0.0.1:8000
```

You can check the API docs at:

```
http://127.0.0.1:8000/docs
```

---

### 5. Start the Frontend (React + Vite)

Navigate to the frontend folder:

```bash
cd frontEnd(1)/mcMillonReact
npm install
npm run dev
```

The frontend will start at:

```
http://localhost:5173/
```

---

## Project Features

Upload `.docx` documents to the forum  
Files are stored in AWS S3, text is extracted and embedded via OpenAI  
Metadata is stored in PostgreSQL  
Vector embeddings stored in Pinecone for semantic search  
Users can click on documents to download them  
Search using human-language queries and get AI-generated answers based on documents  

---

## Video Demo

A full video walkthrough is available [**HERE**](https://youtu.be/haSOeqZEnzs)


## Notes

- This project assumes you have an AWS S3 bucket, Pinecone account, and OpenAI API key ready.
- Make sure you properly set up CORS
- Only `.docx` files are supported at the moment.

---


