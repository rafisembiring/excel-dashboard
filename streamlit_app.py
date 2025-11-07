import streamlit as st
import pandas as pd
import gender_guesser.detector as gender
from io import BytesIO
import os

# Initialize gender detector
d = gender.Detector()

st.set_page_config(page_title="Excel Filter & Gender Checker", layout="wide")

st.title("Excel Filter & Gender Checker")

# Load default filter words from backend
def load_filter_words():
    path = "filter.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            words = [line.strip().lower() for line in f.readlines() if line.strip()]
        return words
    else:
        return []

default_filter_words = load_filter_words()

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.write("Preview of Uploaded Data")
    st.dataframe(df.head())

    if default_filter_words:
        st.write("Using predefined filter words from backend (filter.txt):")
        st.write(", ".join(default_filter_words))

        if "compt" in df.columns:
            # Filter by words in 'compt'
            filtered_df = df[df["compt"].astype(str).str.lower().apply(
                lambda cell: any(word in cell for word in default_filter_words)
            )]

            st.success(f"Found {len(filtered_df)} matching rows.")
            st.dataframe(filtered_df)

            # Gender detection
            if "first name" in df.columns:
                filtered_df["gender"] = filtered_df["first name"].astype(str).apply(
                    lambda x: d.get_gender(x.split()[0])
                )
                st.write("Gender Detection Results")
                st.dataframe(filtered_df[["first name", "last name", "gender"]])
            else:
                st.warning("'first name' column not found. Please ensure it's named exactly 'first name'.")

            # Write to Excel (original + new sheet)
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Original_Data", index=False)
                filtered_df.to_excel(writer, sheet_name="Filtered_Results", index=False)

            st.success("Filtered data added as a new sheet in the Excel file.")
            st.download_button(
                label="Download Updated Excel File",
                data=output.getvalue(),
                file_name="updated_with_filtered.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("'compt' column not found in your Excel file.")
    else:
        st.error("No filter words found in filter.txt on the backend.")
else:
    st.info("Upload your Excel file above to begin.")

st.markdown("---")
st.caption("Built with Streamlit and Python")
