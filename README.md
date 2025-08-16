This is a FastAPI-Next.js repo

### git clone https://github.com/suzuyu33z/Practical_10.git

■ backend

cd backend
python3 -m venv backend_env

source backend_env/bin/activate

pip install -r requirements.txt

uvicorn app:app --reload

■ frontend

cd frontend
npm install
npm run dev

■ http://localhost:3000/customers にアクセス
