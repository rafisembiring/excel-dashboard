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

# Precompile a single big regex for fast vectorized search
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
    df = pd.read_excel(uploaded_file, dtype=str)  # read as strings to avoid dtype inference cost
    df = df.fillna("")  # fill NaN early

    st.write("### Preview of Uploaded Data")
    st.dataframe(df.head())

    if filter_pattern and "compt" in df.columns:
        st.write("### Active Filter Keywords")
        st.text(", ".join(sorted(expanded_filters)))

        # Vectorized filtering using str.contains (fast C-based)
        filtered_df = df[df["compt"].str.lower().str.contains(filter_pattern, na=False, regex=True)]

        st.success(f"Found {len(filtered_df):,} matching rows.")
        st.dataframe(filtered_df.head(50))  # limit preview for large files

        # -------------------------------
        # GENDER DETECTION (optional)
        # -------------------------------
        if "first name" in filtered_df.columns:
            d = gender.Detector(case_sensitive=False)
            # Apply only to unique first names for speed
            unique_firsts = filtered_df["first name"].astype(str).str.split().str[0].unique()
            gender_map = {name: d.get_gender(name) for name in unique_firsts}
            filtered_df["gender"] = filtered_df["first name"].astype(str).str.split().str[0].map(gender_map)

            st.write("### Gender Detection Results (sample)")
            st.dataframe(filtered_df[["first name", "gender"]].head(50))
        else:
            st.warning("'first name' column not found — gender detection skipped.")

        # -------------------------------
        # EXPORT TO EXCEL (same file + new sheet)
        # -------------------------------
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Original_Data", index=False)
            filtered_df.to_excel(writer, sheet_name="Filtered_Results", index=False)

        st.success("Filtered data added as a new sheet in the Excel file.")
        st.download_button(
            label="📥 Download Updated Excel File",
            data=output.getvalue(),
            file_name="updated_with_filtered.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    elif "compt" not in df.columns:
        st.error("'compt' column not found in your Excel file.")
    else:
        st.error("No filter words found in filter.txt or translations.")
else:
    st.info("Upload your Excel file above to begin.")

st.markdown("---")
st.caption("Built with Streamlit and Python | Optimized for 100k+ rows | Created by Rafi Sembiring")
