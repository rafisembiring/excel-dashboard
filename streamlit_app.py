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
# LOAD FILTER WORDS (English)
# -------------------------------
def load_filter_words():
    path = "filter.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip().lower() for line in f if line.strip()]
    return []

default_filter_words = load_filter_words()

# -------------------------------
# LOAD TRANSLATIONS (Optional)
# -------------------------------
def load_translations():
    path = "filter_translations.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

filter_translations = load_translations()

# -------------------------------
# EXPAND FILTERS WITH TRANSLATIONS
# -------------------------------
expanded_filters = set(default_filter_words)
for base_word, translations in filter_translations.items():
    expanded_filters.add(base_word.lower())
    for t in translations:
        expanded_filters.add(t.lower())

# -------------------------------
# FILE UPLOADER
# -------------------------------
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

# -------------------------------
# MAIN LOGIC
# -------------------------------
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.write("### Preview of Uploaded Data")
    st.dataframe(df.head())

    if expanded_filters:
        st.write("### Active Filter Keywords")
        st.write(", ".join(sorted(expanded_filters)))

        if "compt" in df.columns:
            # Whole-word regex filter
            def matches_filter(cell):
                cell = str(cell).lower()
                for word in expanded_filters:
                    pattern = r"\b" + re.escape(word) + r"\b"
                    if re.search(pattern, cell):
                        return True
                return False

            filtered_df = df[df["compt"].apply(matches_filter)]

            st.success(f"Found {len(filtered_df)} matching rows.")
            st.dataframe(filtered_df)

            # -------------------------------
            # GENDER DETECTION (optional)
            # -------------------------------
            d = gender.Detector()

            if "first name" in df.columns:
                filtered_df["gender"] = filtered_df["first name"].astype(str).apply(
                    lambda x: d.get_gender(x.split()[0])
                )
                st.write("### Gender Detection Results")
                st.dataframe(filtered_df[["first name", "last name", "gender"]])
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

        else:
            st.error("'compt' column not found in your Excel file.")
    else:
        st.error("No filter words found in filter.txt or translations.")
else:
    st.info("Upload your Excel file above to begin.")

st.markdown("---")
st.caption("Built with Streamlit and Python | Supports multilingual filters | Created by Rafi Sembiring")

