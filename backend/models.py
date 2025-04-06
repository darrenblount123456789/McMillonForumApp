from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)  # Original file name
    s3_file_name = Column(String, nullable=False)  # UUID file name (used for S3)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # Stores full S3 URL
    text_content = Column(Text, nullable=True)  # Extracted text for search
    uploaded_at = Column(TIMESTAMP, server_default=func.now())

    comments = relationship("Comment", back_populates="document")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    document = relationship("Document", back_populates="comments")
