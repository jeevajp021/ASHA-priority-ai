## Setup Instructions

### Backend
cd backend
python -m venv venv
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload

### Frontend
cd frontend
npm install
npm run dev