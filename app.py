import streamlit as st
import pandas as pd
import plotly.express as px
from src import database, crud, analysis

# Page Config
st.set_page_config(page_title="Loblaw Bio Analysis", layout="wide")

# Data Loading (cached)
@st.cache_resource
def setup_database():
    crud.init_db()
    db = database.SessionLocal()
    crud.load_data(db, "cell-count.csv")
    return db

db = setup_database()

@st.cache_data
def load_dataframe():
    with database.SessionLocal() as session:
        return crud.get_data_as_dataframe(session)

df_raw = load_dataframe()
df_processed = analysis.calculate_frequencies(df_raw)

# Sidebar filters
st.sidebar.title("Table Filters")
sample_type_options = ["All"] + list(df_processed['sample_type'].unique())
sample_type_filter = st.sidebar.selectbox("Sample Type", sample_type_options, index=0)
treatment_filter = st.sidebar.selectbox("Treatment", ["All"] + list(df_processed['treatment'].unique()))
condition_filter = st.sidebar.selectbox("Condition", ["All"] + list(df_processed['condition'].unique()))

# Apply filters
filtered_df = df_processed.copy()
if sample_type_filter != "All":
    filtered_df = filtered_df[filtered_df['sample_type'] == sample_type_filter]
if treatment_filter != "All":
    filtered_df = filtered_df[filtered_df['treatment'] == treatment_filter]
if condition_filter != "All":
    filtered_df = filtered_df[filtered_df['condition'] == condition_filter]

# Main Dashboard
st.title("Loblaw Bio: Clinical Trial Dashboard")

tab1, tab2, tab3 = st.tabs(["Data Overview", "Statistical Analysis", "Data Subset Analysis"])

with tab1:
    # High-level metrics breakdown
    st.markdown("### High-Level Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    unique_samples = filtered_df['sample_id'].nunique()
    unique_subjects = filtered_df['subject'].nunique()
    responders = filtered_df[filtered_df['response'] == 'yes']['subject'].nunique()
    
    col1.metric("Total Samples", unique_samples)
    col2.metric("Total Subjects", unique_subjects)
    col3.metric("Responders", responders)
    col4.metric("Avg Age", f"{filtered_df['age'].mean():.1f}")

    st.markdown("---")
    
    # Summary Table
    st.markdown("### Cell Frequency Summary Table")
    st.caption("Breakdown of relative frequency per sample (one row per cell population).")
    
    summary_table = filtered_df[[
        'sample_id', 'total_count', 'cell_type', 'count', 'percentage'
    ]].copy()
    
    summary_table.columns = ['sample', 'total_count', 'population', 'count', 'percentage']
    
    st.dataframe(
        summary_table,
        column_config={
            "sample": "Sample ID",
            "total_count": "Total Cells",
            "population": "Population",
            "count": "Count",
            "percentage": st.column_config.NumberColumn(
                "Frequency (%)",
                format="%.2f %%" 
            )
        },
        use_container_width=True,
        hide_index=True,
        height=300
    )

with tab2:
    st.info("**Analysis limited to**: Melanoma patients, PBMC samples, Miraclib treatment")

    st.markdown("### Cell Population Distributions")
    part3_data = df_processed[
        (df_processed['condition'].str.lower() == 'melanoma') &
        (df_processed['sample_type'].str.lower() == 'pbmc') &
        (df_processed['treatment'].str.lower() == 'miraclib')
    ]

    fig = px.box(
        part3_data, 
        x="cell_type", 
        y="percentage", 
        color="response",
        title="Relative Frequency by Response (Melanoma PBMC - Miraclib)",
        points="outliers",
        hover_data=["sample_id", "subject"]
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Responder vs. Non-Responder Analysis")
    st.caption("Statistical Test: Mann-Whitney U (Non-parametric test for independent samples)")
    
    results = []
    if not part3_data.empty:
        cell_types = part3_data['cell_type'].unique()
        
        for ct in cell_types:
            stat, p_val = analysis.run_mann_whitney(part3_data, ct)
            if p_val is not None:
                results.append({
                    "Cell Population": ct,
                    "P-Value": p_val,
                    "Significant (p<0.05)": "Yes" if p_val < 0.05 else "No"
                })
    
    if results:
        results_df = pd.DataFrame(results)

        def highlight_rows(row):
            value = row["Significant (p<0.05)"]
            if value == "Yes":
                return ['background-color: #d4edda; color: #155724'] * len(row)
            elif value == "No":
                return ['background-color: #f8d7da; color: #721c24'] * len(row)
            return [''] * len(row)

        st.table(results_df.style.apply(highlight_rows, axis=1))
    else:
        st.warning("Insufficient data for statistical analysis.")

with tab3:
    st.info("**Analysis limited to**: Melanoma patients, PBMC samples, Miraclib treatment, Baseline (time_from_treatment_start=0)")
    st.markdown("### Subset Analysis - Early Treatment Effects")
    
    answers = analysis.get_part4_answers(df_processed)
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("##### Samples per Project")
        if answers['samples_per_proj']:
            proj_df = pd.DataFrame(
                list(answers['samples_per_proj'].items()), 
                columns=['Project', 'Sample Count']
            )
            st.dataframe(proj_df, use_container_width=True, hide_index=True)
        else:
            st.write("No data")
    
    with c2:
        st.markdown("##### Response Status")
        if answers['response_counts']:
            resp_df = pd.DataFrame(
                list(answers['response_counts'].items()), 
                columns=['Response', 'Subject Count']
            )
            st.dataframe(resp_df, use_container_width=True, hide_index=True)
        else:
            st.write("No data")
    
    with c3:
        st.markdown("##### Gender Distribution")
        if answers['sex_counts']:
            sex_df = pd.DataFrame(
                list(answers['sex_counts'].items()), 
                columns=['Gender', 'Subject Count']
            )
            st.dataframe(sex_df, use_container_width=True, hide_index=True)
        else:
            st.write("No data")