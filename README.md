# eCFR Explorer

A simple interactive tool for searching and analyzing the Electronic Code of Federal Regulations (eCFR), built with FastAPI and Streamlit.
---

## 📁 Project Structure

MyProject/
├── backend/ # FastAPI backend service
│ └── main.py # API routes to search and return word count stats
├── frontend/ # Streamlit frontend app
│ └── streamlit_app.py # User interface with interactive visualizations
├── data/ # Folder containing the eCFR CSV dataset
│ └── ecfr_chunks_all_titles.csv
├── data_processing.py # Optional: helper scripts to clean/process data
├── ecfr_app.py # (Optional) entry-point or test script
├── ecfr_project.ipynb # (Optional) notebook for data exploration
└── README.md # This documentation file


---

## ⚙️ Requirements

Make sure Python 3.8+ is installed. Then install dependencies:

```bash
pip install fastapi uvicorn streamlit pandas plotly requests

