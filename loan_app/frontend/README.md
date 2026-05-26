# Loan Prediction Frontend + Vercel Deployment

This directory contains the Next.js frontend and the Python serverless API for Vercel.

## Deploying on Vercel

1. Push this repository to GitHub.
2. Create a new project on Vercel.
3. Select the GitHub repository and choose the `loan_app/frontend` folder as the root directory.
4. Use the following settings:
   - Framework Preset: `Next.js`
   - Root Directory: `loan_app/frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

Vercel will detect the `api/` directory and deploy `frontend/api/predict.py` as a Python serverless function.

## Local testing

Install dependencies:

```bash
cd "d:/ROOT/Loan Prediction/loan_app/frontend"
npm install
```

Run the frontend locally:

```bash
npm run dev
```

Then open:

```bash
http://localhost:3000
```

## Notes

- The frontend sends prediction requests to `/api/predict`.
- The Python serverless function loads the model from `frontend/model/loan_model.pkl`.
- If you deploy on Vercel, both the frontend and the API are served from the same domain.
