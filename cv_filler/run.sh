#\!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt -q
echo "Starting CV Vorlage Filler..."
echo "Open: http://localhost:8501"
streamlit run app.py --server.headless false --browser.gatherUsageStats false
