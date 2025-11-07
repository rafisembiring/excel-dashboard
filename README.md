Excel Filter & Gender Checker Dashboard
=======================================

Overview
--------
This Streamlit app filters company data from an Excel file based on a predefined list of words in the 'compt' column and adds gender information from the 'first name' column.

Features
--------
- Upload Excel files (.xlsx or .xls)
- Automatically filters rows using backend-defined words from filter.txt
- Adds gender detection based on first name
- Saves filtered data as a new sheet in the same Excel file
- Download the updated Excel file

File Structure
--------------
excel-filter-dashboard/
│
├── app.py
├── filter.txt
├── requirements.txt
├── README.txt
└── .gitignore

How to Run Locally
------------------
1. Install dependencies:
   pip install -r requirements.txt

2. Start the Streamlit app:
   streamlit run app.py

3. Open your browser at:
   http://localhost:8501

Deploy on Streamlit Cloud
-------------------------
1. Push this folder to a public GitHub repository.

2. Go to:
   https://share.streamlit.io

3. Connect your GitHub account and select the repository.

4. Choose app.py as the main file and click "Deploy".

After deployment, the app will be hosted publicly at:
   https://excel-filtering-company.streamlit.app/

Usage
-----
1. Upload your Excel file.
2. The app automatically filters based on filter.txt (in the backend).
3. The result is added as a new sheet named "Filtered_Results" in the same Excel file.
4. Download the updated Excel file with one click.

Notes
-----
- The filter words are stored in filter.txt and loaded automatically by the backend.
- The 'compt' column must exist in your Excel file for filtering to work.
- The 'first name' column is required for gender detection.
- All processing runs within Streamlit, no data is stored externally.

License
-------

This project is free to use for personal and educational purposes.
