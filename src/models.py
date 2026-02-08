from sqlalchemy import Column, Integer, String, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from .database import Base

class CellType(Base):
    """
    Lookup table for cell populations.
    Standardizes names and saves space (Integer FK vs repeated Strings).
    """
    __tablename__ = 'cell_types'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    counts = relationship("CellCount", back_populates="cell_type_rel")

class Sample(Base):
    __tablename__ = 'samples'
    
    sample_id = Column(String, primary_key=True, index=True)
    project = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    condition = Column(String)
    age = Column(Integer)
    sex = Column(String)
    treatment = Column(String)
    response = Column(String)
    sample_type = Column(String)
    time_from_treatment_start = Column(Integer)

    counts = relationship("CellCount", back_populates="sample")

    # Composite index
    __table_args__ = (
        Index('idx_filtering', 'condition', 'treatment', 'sample_type'),
    )

class CellCount(Base):
    __tablename__ = 'cell_counts'
    
    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String, ForeignKey('samples.sample_id'), nullable=False)
    cell_type_id = Column(Integer, ForeignKey('cell_types.id'), nullable=False)
    count = Column(Integer, CheckConstraint('count >= 0'), nullable=False)
    
    sample = relationship("Sample", back_populates="counts")
    cell_type_rel = relationship("CellType", back_populates="counts")