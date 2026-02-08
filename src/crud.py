import pandas as pd
from sqlalchemy.orm import Session
from . import models, database

def init_db():
    """Create tables in the database."""
    models.Base.metadata.create_all(bind=database.engine)

def load_data(db: Session, csv_path: str):
    """
    Parses CSV and loads it into the normalized database schema.
    """
    if db.query(models.Sample).first():
        return

    df = pd.read_csv(csv_path)
    
    cell_type_names = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
    
    type_map = {}
    for name in cell_type_names:
        ct = models.CellType(name=name)
        db.add(ct)
        db.flush() # Flush to get the auto-generated ID
        type_map[name] = ct.id
    
    meta_cols = [c for c in df.columns if c not in cell_type_names]
    samples_df = df[meta_cols].rename(columns={'sample': 'sample_id'}).drop_duplicates(subset='sample_id')
    
    db.bulk_insert_mappings(models.Sample, samples_df.to_dict(orient='records'))
    
    # Melt to long format
    counts_df = df.melt(id_vars=['sample'], value_vars=cell_type_names, 
                        var_name='cell_type_name', value_name='count')
    
    counts_df['cell_type_id'] = counts_df['cell_type_name'].map(type_map)
    counts_df = counts_df.rename(columns={'sample': 'sample_id'})
    
    counts_data = counts_df[['sample_id', 'cell_type_id', 'count']].to_dict(orient='records')
    
    db.bulk_insert_mappings(models.CellCount, counts_data)
    db.commit()

def get_data_as_dataframe(db: Session):
    """
    Joins Sample, CellCount, and CellType tables to return a flat DataFrame.
    """
    query = db.query(
        models.Sample.sample_id, 
        models.Sample.project, 
        models.Sample.subject,
        models.Sample.condition, 
        models.Sample.treatment, 
        models.Sample.response,
        models.Sample.sample_type, 
        models.Sample.time_from_treatment_start, 
        models.Sample.sex,
        models.Sample.age,
        models.CellType.name.label("cell_type"),
        models.CellCount.count
    ).join(models.CellCount, models.Sample.sample_id == models.CellCount.sample_id)\
     .join(models.CellType, models.CellCount.cell_type_id == models.CellType.id)
    
    df = pd.read_sql(query.statement, db.bind)
    return df