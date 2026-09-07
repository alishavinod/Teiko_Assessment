import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from analysis import (
    get_frequency_summary,
    compare_responders,
    get_baseline_analysis
)


st.title("Clinical Trial Cell Count Analysis")

st.write(
    "Analysis of immune cell populations in melanoma PBMC samples "
    "from patients treated with miraclib."
)

# -------------------------
# Part 2: Data Overview
# -------------------------

st.header("1. Data Overview")

summary = get_frequency_summary()

st.dataframe(summary)


# -------------------------
# Part 3: Statistical Analysis
# -------------------------

st.header("2. Responder vs Non-Responder Analysis")

stats = compare_responders()

st.dataframe(stats)

st.subheader("Relative Frequencies")

plot_data = summary.copy()

# Get only melanoma PBMC miraclib samples
# We need response information for the plot
# Re-read it from the database
import sqlite3

conn = sqlite3.connect("cell_counts.db")

df = pd.read_sql_query("""
    SELECT *
    FROM samples
    WHERE condition = 'melanoma'
      AND sample_type = 'PBMC'
      AND treatment = 'miraclib'
""", conn)

conn.close()

df["total_count"] = df[
    ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
].sum(axis=1)

for population in [
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte"
]:
    df[population] = df[population] / df["total_count"] * 100

plot_data = df.melt(
    id_vars=["response"],
    value_vars=[
        "b_cell",
        "cd8_t_cell",
        "cd4_t_cell",
        "nk_cell",
        "monocyte"
    ],
    var_name="population",
    value_name="percentage"
)

fig, ax = plt.subplots(figsize=(10, 6))

sns.boxplot(
    data=plot_data,
    x="population",
    y="percentage",
    hue="response",
    ax=ax
)

ax.set_xlabel("Immune Cell Population")
ax.set_ylabel("Relative Frequency (%)")
ax.set_title("Miraclib Responders vs Non-Responders")

st.pyplot(fig)


st.write(
    "**Significant population:** CD4 T cells "
    "(Mann–Whitney U test, p = 0.0133)."
)


# -------------------------
# Part 4: Baseline Analysis
# -------------------------

st.header("3. Baseline Sample Analysis")

st.write(
    "Melanoma PBMC samples from miraclib-treated patients "
    "at treatment start (time = 0)."
)

projects, responses, sexes = get_baseline_analysis()

st.subheader("Samples per Project")
st.dataframe(projects.rename("sample_count"))

st.subheader("Subjects by Response")
st.dataframe(responses.rename("subject_count"))

st.subheader("Subjects by Sex")
st.dataframe(sexes.rename("subject_count"))


# -------------------------
# AI Models
# -------------------------

st.header("4. AI Models")

st.write("Quintazide")