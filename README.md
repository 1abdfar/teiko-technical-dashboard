# Teiko Teiknical: Clinical Trial Analysis Dashboard

**By:** Abdallah Fares

This is my submission for the Teiko Labs bioinformatics engineering technical assessment.

## Quick Start

### Running in GitHub Codespaces
1. Open this repository in Codespaces
2. Dependencies should install automatically. If not:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the dashboard:
   ```bash
   streamlit run app.py
   ```
4. Codespaces will provide a link to view the app in your browser

## Project Structure
```
├── app.py                  # Streamlit dashboard
├── src/
│   ├── database.py         # SQLite setup
│   ├── models.py           # Database schema
│   ├── crud.py             # Data loading & queries
│   └── analysis.py         # Statistical functions
├── tests/
│   └── test_analysis.py    # Unit tests
└── cell-count.csv          # Input data
```

### Code Organization

I organized the code into separate modules to keep things clean:

- **`app.py`**: Handles all the UI and visualization. I used Streamlit to build a functional interface quickly, but the backend logic is separated out so it could easily be converted to a REST API for a React frontend later.

- **`src/crud.py` and `src/database.py`**: These handle all database operations. The `bulk_insert_mappings` function makes data loading fast even with thousands of rows.

- **`src/analysis.py`**: Statistical functions live here. Separation makes it easy to test individual functions.

- **`src/models.py`**: Defines the database schema using SQLAlchemy ORM. Gives us type safety and makes the code more maintainable.

## Database Schema

### Design

The database uses three tables in a normalized structure:

**`samples`** (Main metadata table)
- Primary key: `sample_id`
- Stores patient info: project, subject, condition, treatment, response, demographics
- Indexed on commonly filtered columns for fast queries

**`cell_types`** (Lookup table)
- Maps cell population names (e.g., "b_cell") to integer IDs
- Saves storage space since we reference the ID instead of repeating strings

**`cell_counts`** (Measurement data)
- Links samples to cell types with actual count values
- Foreign keys to both `samples` and `cell_types` tables
- Stores data in "long" format (one row per cell type per sample)

I chose a normalized schema because it scales better than storing everything in a wide table. In a wide format, adding a new cell population (like macrophages) would require altering the table schema, but with this design I just insert a new row in `cell_types` with no downtime. The composite index on `(condition, treatment, sample_type)` makes filtering queries fast even with thousands of samples, and using the `cell_types` lookup table avoids storing repeated strings, which reduces database size. The long format also makes it easy to aggregate data (e.g., "average B cells across all melanoma patients") without dynamically generating SQL for each cell type. Foreign keys enforce data integrity by preventing invalid entries, like a sample referencing a cell type that doesn't exist.

If this scaled to hundreds of projects and thousands of samples, the main bottleneck would probably be the Streamlit caching, not the database itself. I'd consider adding database partitioning by project or time period if query times got slow. For production use with millions of rows, I'd add chunk-based processing and switch to PostgreSQL for better performance.

As for the statistical test in Part 3, I used the Mann-Whitney U test to compare cell frequencies between responders and non-responders. I chose this non-parametric test since it doesn't assume normal distributions, which appears appropriate for flow cytometry data that can have outliers.

## Testing

I included a basic unit test (`tests/test_analysis.py`) that verifies the percentage calculation logic. For a production system, I'd add more tests covering:
- Edge cases (empty samples, missing data)
- Statistical function accuracy
- Database constraint validation

Run tests with:
```bash
pytest tests/
```

