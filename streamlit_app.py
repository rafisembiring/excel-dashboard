import streamlit as st
import pandas as pd
import gender_guesser.detector as gender
import re
import os
import json
from io import BytesIO

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------
st.set_page_config(page_title="Excel Filter & Gender Checker", layout="wide")
st.title("Excel Filter & Gender Checker")

# -------------------------------
# LOAD FILTER WORDS
# -------------------------------
@st.cache_data
def load_filter_words():
    path = "filter.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip().lower() for line in f if line.strip()]
    return []

@st.cache_data
def load_translations():
    path = "filter_translations.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

default_filter_words = load_filter_words()
filter_translations = load_translations()

# -------------------------------
# EXPAND FILTERS
# -------------------------------
expanded_filters = set(default_filter_words)
for base_word, translations in filter_translations.items():
    expanded_filters.add(base_word.lower())
    expanded_filters.update([t.lower() for t in translations])

filter_pattern = (
    r"\b(" + "|".join(re.escape(word) for word in expanded_filters) + r")\b"
    if expanded_filters
    else None
)

# -------------------------------
# FILE UPLOADER
# -------------------------------
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

# -------------------------------
# MAIN LOGIC
# -------------------------------
if uploaded_file is not None:
    # Extract original filename
    original_filename = os.path.splitext(uploaded_file.name)[0]

    df = pd.read_excel(uploaded_file, dtype=str).fillna("")

    st.write("### Preview of Uploaded Data")
    st.dataframe(df.head())

    # -------------------------------
    # GENDER DETECTION (for ALL ROWS)
    # -------------------------------
    if "first name" in df.columns:
        st.write("### Detecting Gender for All Rows...")
        d = gender.Detector(case_sensitive=False)

        first_names = (
            df["first name"]
            .astype(str)
            .str.strip()
            .str.split()
            .str[0]
            .fillna("")
        )

        unique_firsts = [n for n in first_names.unique() if n and n.isalpha()]

        gender_map = {}
        for name in unique_firsts:
            try:
                gender_map[name] = d.get_gender(name.lower())
            except Exception:
                gender_map[name] = "unknown"

        df["gender"] = first_names.map(gender_map).fillna("unknown")

        st.success(f"Gender detected for {len(unique_firsts):,} unique names.")
        st.dataframe(df[["first name", "gender"]].head(20))
    else:
        st.warning("'first name' column not found — gender detection skipped.")

    # -------------------------------
    # FILTERING (after gender detection)
    # -------------------------------
    if filter_pattern and "compt" in df.columns:
        st.write("### Active Filter Keywords")
        st.text(", ".join(sorted(expanded_filters)))

        # Filter rows matching pattern
        filtered_df = df[df["compt"].str.lower().str.contains(filter_pattern, na=False, regex=True)]

        # Remove filtered rows from main dataframe
        remaining_df = df[~df.index.isin(filtered_df.index)]

        st.success(f"Found {len(filtered_df):,} matching rows. {len(remaining_df):,} rows remain.")
        st.dataframe(filtered_df.head(50))
    else:
        filtered_df = pd.DataFrame()
        remaining_df = df
        st.warning("No valid filter pattern or 'compt' column missing.")

    # -------------------------------
    # EXPORT TO EXCEL (REMAINING + FILTERED)
    # -------------------------------
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        remaining_df.to_excel(writer, sheet_name="All_Data_With_Gender", index=False)
        if not filtered_df.empty:
            filtered_df.to_excel(writer, sheet_name="Filtered_Results", index=False)

    st.success("Filtered companies moved to a separate sheet successfully.")

    # File name with _filtered suffix
    output_filename = f"{original_filename}_filtered.xlsx"

    st.download_button(
        label="📥 Download Filtered Excel File",
        data=output.getvalue(),
        file_name=output_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Upload your Excel file above to begin.")

st.markdown("---")
st.caption("Built with Streamlit and Python | Optimized for 100k+ rows | Created by Rafi Sembiring")
