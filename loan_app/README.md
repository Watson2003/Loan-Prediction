# Loan Approval Prediction App

## Backend (FastAPI)

Install required Python packages:

```bash
cd "d:/ROOT/Loan Prediction/loan_app"
python -m pip install -r requirements.txt
```

Start the FastAPI backend:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Then open the backend UI at:

```
http://localhost:8000/
```

## Frontend (Next.js)

Install frontend dependencies:

```bash
cd "d:/ROOT/Loan Prediction/loan_app/frontend"
npm install
```

Start the Next.js development server:

```bash
npm run dev
```

Then open the frontend UI at:

```
http://localhost:3000/
```

## Notes

- The backend loads the model from `loan_app/model/loan_model.pkl`.
- The form accepts the same features used during training.
- If the FastAPI backend is not running, the frontend will show a connection error.
