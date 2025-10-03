"""
Document Manager Models

SQLAlchemy models for document management system with hierarchical relationships.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from shared_models.models import Base


# Association table for many-to-many relationship between documents (children)
document_children = Table(
    'document_children',
    Base.metadata,
    Column('parent_id', UUID(as_uuid=True), ForeignKey('documents.id'), primary_key=True),
    Column('child_id', UUID(as_uuid=True), ForeignKey('documents.id'), primary_key=True)
)


class Document(Base):
    """
    Document model for managing documents with hierarchical relationships
    
    Supports:
    - Parent-child relationships (many-to-many)
    - User ownership
    - Document metadata and versioning
    """
    __tablename__ = 'documents'
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique document identifier"
    )
    
    # Document UUID (business identifier)
    doc_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Business document identifier"
    )
    
    # User relationship (foreign key)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        doc="Owner user ID"
    )
    
    # Parent document (self-referential)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('documents.id', ondelete='SET NULL'),
        nullable=True,
        doc="Parent document ID for hierarchical structure"
    )
    
    # Document metadata
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Document title"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Document description"
    )
    
    file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="Path to the document file"
    )
    
    file_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Original file name"
    )
    
    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="File size in bytes"
    )
    
    mime_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="MIME type of the document"
    )
    
    # Document status and version
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        doc="Document version number"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether document is active"
    )
    
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether document is publicly accessible"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Document creation timestamp"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Document last update timestamp"
    )
    
    # Processing metadata
    processing_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Document processing status (pending, processing, completed, failed)"
    )
    
    processing_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Error message if processing failed"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="documents",
        doc="Document owner"
    )
    
    # Parent-child relationships
    parent = relationship(
        "Document",
        remote_side=[id],
        back_populates="direct_children",
        doc="Parent document"
    )
    
    direct_children = relationship(
        "Document",
        back_populates="parent",
        cascade="all, delete-orphan",
        doc="Direct child documents"
    )
    
    # Many-to-many children relationship
    children: Mapped[List["Document"]] = relationship(
        "Document",
        secondary=document_children,
        primaryjoin=id == document_children.c.parent_id,
        secondaryjoin=id == document_children.c.child_id,
        back_populates="parents",
        doc="Child documents (many-to-many)"
    )
    
    parents: Mapped[List["Document"]] = relationship(
        "Document",
        secondary=document_children,
        primaryjoin=id == document_children.c.child_id,
        secondaryjoin=id == document_children.c.parent_id,
        back_populates="children",
        doc="Parent documents (many-to-many)"
    )
    
    def __repr__(self) -> str:
        return f"<Document(id={self.id}, doc_id={self.doc_id}, title='{self.title}', user_id={self.user_id})>"
    
    def __str__(self) -> str:
        return f"Document: {self.title} ({self.doc_id})"
    
    @property
    def is_root(self) -> bool:
        """Check if document is a root document (no parent)"""
        return self.parent_id is None
    
    @property
    def has_children(self) -> bool:
        """Check if document has any children"""
        return len(self.children) > 0 or len(self.direct_children) > 0
    
    def get_all_children(self) -> List["Document"]:
        """Get all children including both direct and many-to-many relationships"""
        all_children = list(self.direct_children)
        all_children.extend(self.children)
        # Remove duplicates
        seen = set()
        unique_children = []
        for child in all_children:
            if child.id not in seen:
                seen.add(child.id)
                unique_children.append(child)
        return unique_children
    
    def get_all_parents(self) -> List["Document"]:
        """Get all parents including both direct and many-to-many relationships"""
        all_parents = []
        if self.parent:
            all_parents.append(self.parent)
        all_parents.extend(self.parents)
        # Remove duplicates
        seen = set()
        unique_parents = []
        for parent in all_parents:
            if parent.id not in seen:
                seen.add(parent.id)
                unique_parents.append(parent)
        return unique_parents


class DocumentVersion(Base):
    """
    Document version history model for tracking document changes
    """
    __tablename__ = 'document_versions'
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Version record ID"
    )
    
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('documents.id', ondelete='CASCADE'),
        nullable=False,
        doc="Reference to the document"
    )
    
    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Version number"
    )
    
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Document title at this version"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Document description at this version"
    )
    
    file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="File path at this version"
    )
    
    changes_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Summary of changes in this version"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Version creation timestamp"
    )
    
    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        doc="User who created this version"
    )
    
    # Relationships
    document = relationship(
        "Document",
        back_populates="versions",
        doc="Associated document"
    )
    
    creator = relationship(
        "User",
        doc="User who created this version"
    )
    
    def __repr__(self) -> str:
        return f"<DocumentVersion(id={self.id}, document_id={self.document_id}, version={self.version_number})>"


# Add back-reference to Document model
Document.versions = relationship(
    "DocumentVersion",
    back_populates="document",
    cascade="all, delete-orphan",
    order_by=DocumentVersion.version_number,
    doc="Document version history"
)
