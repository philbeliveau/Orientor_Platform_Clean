"""
Base Model Classes for Orientor Platform

Provides standardized base classes with proper autoincrement configuration
to prevent the systemic autoincrement issues discovered in the database architecture.
"""

from sqlalchemy import Column, Integer, DateTime, func
from ..utils.database import Base


class AutoIncrementBase(Base):
    """
    Abstract base class providing standard auto-incrementing primary key.
    
    This class ensures all derived models have proper autoincrement configuration
    for PostgreSQL compatibility. All models should inherit from this class instead
    of directly from Base to prevent autoincrement issues.
    
    Key Features:
    - Properly configured auto-incrementing primary key
    - PostgreSQL SERIAL compatibility  
    - Standardized timestamp fields
    - Abstract class (cannot be instantiated directly)
    """
    
    __abstract__ = True  # This makes it an abstract base class
    
    # Standard auto-incrementing primary key - NEVER override without autoincrement=True
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Standard timestamp fields for all models
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class SimpleAutoIncrementBase(Base):
    """
    Minimal base class with just auto-incrementing primary key.
    
    Use this for models that need custom timestamp handling or
    don't want the standard created_at/updated_at fields.
    """
    
    __abstract__ = True
    
    # Standard auto-incrementing primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)


class UUIDBase(Base):
    """
    Base class for models that use UUID primary keys instead of integers.
    
    Use this for models that require UUID primary keys (like distributed systems,
    public-facing identifiers, etc.)
    """
    
    __abstract__ = True
    
    from sqlalchemy.dialects.postgresql import UUID
    import uuid
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


# Migration Guide:
"""
HOW TO USE THESE BASE CLASSES:

1. NEW MODELS (Recommended approach):
   ```python
   from .base_model import AutoIncrementBase
   
   class MyNewModel(AutoIncrementBase):
       __tablename__ = "my_new_table"
       
       # Your model fields here - DON'T define id, it's inherited
       name = Column(String(100), nullable=False)
       # created_at and updated_at are also inherited
   ```

2. EXISTING MODELS (Gradual migration):
   ```python
   # Current (works but not future-proof):
   class MyExistingModel(Base):
       id = Column(Integer, primary_key=True, index=True, autoincrement=True)
       # ... rest of model
   
   # Better (future-proof):
   class MyExistingModel(SimpleAutoIncrementBase):
       # Remove the id line - it's inherited
       # ... rest of model
   ```

3. UUID MODELS:
   ```python
   from .base_model import UUIDBase
   
   class MyUUIDModel(UUIDBase):
       __tablename__ = "my_uuid_table"
       # id, created_at, updated_at are inherited
       # ... your fields here
   ```

MIGRATION BENEFITS:
- Prevents autoincrement issues automatically
- Ensures consistent primary key patterns
- Standardizes timestamp handling
- Makes code review easier (check for Base vs AutoIncrementBase)
- Reduces boilerplate code
"""