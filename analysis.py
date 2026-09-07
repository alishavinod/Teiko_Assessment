import sqlite3
import pandas as pd
from scipy.stats import mannwhitneyu
import matplotlib.pyplot as plt
import seaborn as sns

DB_FILE = "cell_counts.db"

POPULATIONS = [
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte"
]


def get_frequency_summary():
    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query("SELECT * FROM samples", conn)

    conn.close()

    # Total cell count for each sample
    df["total_count"] = df[POPULATIONS].sum(axis=1)

    # Convert population columns into rows
    summary = df.melt(
        id_vars=["sample", "total_count"],
        value_vars=POPULATIONS,
        var_name="population",
        value_name="count"
    )

    # Calculate relative frequency
    summary["percentage"] = (
        summary["count"] / summary["total_count"] * 100
    )

    return summary


def compare_responders():
    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query("""
        SELECT *
        FROM samples
        WHERE condition = 'melanoma'
          AND sample_type = 'PBMC'
          AND treatment = 'miraclib'
    """, conn)

    conn.close()

    # Calculate total cell count
    df["total_count"] = df[POPULATIONS].sum(axis=1)

    results = []

    for population in POPULATIONS:
        # Convert counts to percentages
        percentages = df[population] / df["total_count"] * 100

        responders = percentages[df["response"] == "yes"]
        non_responders = percentages[df["response"] == "no"]

        statistic, p_value = mannwhitneyu(
            responders,
            non_responders,
            alternative="two-sided"
        )

        results.append({
            "population": population,
            "responders_median": responders.median(),
            "non_responders_median": non_responders.median(),
            "U_statistic": statistic,
            "p_value": p_value
        })

    return pd.DataFrame(results)

def plot_boxplots():
    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query("""
        SELECT *
        FROM samples
        WHERE condition = 'melanoma'
          AND sample_type = 'PBMC'
          AND treatment = 'miraclib'
    """, conn)

    conn.close()

    # Calculate total count
    df["total_count"] = df[POPULATIONS].sum(axis=1)

    # Convert counts to percentages
    for population in POPULATIONS:
        df[population] = df[population] / df["total_count"] * 100

    # Convert to long format
    plot_data = df.melt(
        id_vars=["response"],
        value_vars=POPULATIONS,
        var_name="population",
        value_name="percentage"
    )

    # Create boxplots
    plt.figure(figsize=(10, 6))

    sns.boxplot(
        data=plot_data,
        x="population",
        y="percentage",
        hue="response"
    )

    plt.xlabel("Immune Cell Population")
    plt.ylabel("Relative Frequency (%)")
    plt.title("Immune Cell Frequencies: Miraclib Responders vs Non-Responders")
    plt.tight_layout()

    plt.savefig("boxplots.png")
    plt.show()

def get_baseline_analysis():
    conn = sqlite3.connect(DB_FILE)

    query = """
        SELECT *
        FROM samples
        WHERE condition = 'melanoma'
          AND sample_type = 'PBMC'
          AND treatment = 'miraclib'
          AND time_from_treatment_start = 0
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    project_counts = df.groupby("project").size()

    response_counts = df.groupby("response")["subject"].nunique()

    sex_counts = df.groupby("sex")["subject"].nunique()

    return project_counts, response_counts, sex_counts

if __name__ == "__main__":
    summary = get_frequency_summary()
    print(summary.head(10))

    print("\nStatistical comparison:")
    print(compare_responders())

    print("\nBaseline analysis:")
    projects, responses, sexes = get_baseline_analysis()

    print("\nSamples per project:")
    print(projects)

    print("\nSubjects by response:")
    print(responses)

    print("\nSubjects by sex:")
    print(sexes)

    plot_boxplots()