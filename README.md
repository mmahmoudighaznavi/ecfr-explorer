# eCFR Explorer

A simple interactive tool for searching and analyzing the Electronic Code of Federal Regulations (eCFR), built with FastAPI and Streamlit.
---

## 📁 Project Structure

MyProject/
│
├── ecfr_chunks_all_titles.csv # eCFR dataset (CSV format)
├── main.py # FastAPI backend (API routes)
├── streamlit_app.py # Streamlit frontend (user interface)
├── requirements.txt # Python dependencies
├── README.md # This file


---

## 🔧 Getting Started

### Step 1: Clone the repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

### Step 2: Create a virtual environment
python -m venv venv
source venv/bin/activate       # On Windows use: venv\Scripts\activate

### Step 3: Install dependencies
pip install -r requirements.txt

pip install fastapi uvicorn streamlit pandas plotly requests

### Step 4: Run the backend (FastAPI)
uvicorn main:app --reload

### Step 5: Run the frontend (Streamlit)

streamlit run streamlit_app.py

---

## ⚙️ Requirements

Make sure Python 3.8+ is installed. Then install dependencies:

Notes
The dataset file (ecfr_chunks_all_titles.csv) should be in the root directory.

Make sure both backend and frontend run simultaneously for full functionality.

