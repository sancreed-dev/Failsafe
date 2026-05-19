# FAILSAFE

FAILSAFE is a full-stack student failure prediction system for faculty teams. Upload the UCI student performance datasets, retrain an XGBoost model, review risk dashboards, download PDF reports, and inspect per-student SHAP explanations with intervention suggestions.

## Prerequisites

- **Python 3.11+** with `pip`
- **Node.js 18+** with `npm`

Run every command below from the **project root** (`Failsafe/`), unless noted otherwise.

## Project layout

```text
Failsafe/
├── backend/
│   ├── app.py                 # FastAPI entry point
│   ├── data/uploads/          # student-mat.csv & student-por.csv (bundled)
│   ├── models/                # model.pkl, metrics.json
│   ├── routes/                # API routers
│   └── requirements.txt
└── frontend/                  # React + Vite dashboard
```

Sample UCI CSV files are already in `backend/data/uploads/`, so you can train and run the API without uploading anything first.

## Quick start

### 1. Backend

Install dependencies and train the model:

```bash
python -m pip install -r backend/requirements.txt
python -m backend.models.train_model
```

Start the API (keep this terminal open):

```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Frontend

In a **second terminal**:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open the dashboard: [http://127.0.0.1:5173](http://127.0.0.1:5173) (or [http://localhost:5173](http://localhost:5173))

## Demo login

| Field    | Value                   |
| -------- | ----------------------- |
| Email    | `faculty@failsafe.edu`  |
| Password | `failsafe123`           |

## Features

- Faculty authentication (signed JWT tokens) with protected API routes
- Upload `student-mat.csv` and `student-por.csv` to merge, retrain, and refresh predictions
- XGBoost training with accuracy, precision, recall, F1, and confusion matrix
- Global SHAP summary chart and per-student SHAP explanations
- Plain-English risk reasons and intervention actions
- Faculty analytics, PDF report download, and SQLite snapshots for demo history
- React dashboard with risk cards, charts, student list, and SHAP detail view

## Uploading new data

Use the dashboard upload panel, or call the API with **both** files named exactly:

- `student-mat.csv`
- `student-por.csv`

Form fields: `math_file`, `por_file` (multipart upload, Bearer token required).

Official dataset: [UCI Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance)

## Environment variables (optional)

| Variable                 | Default                         | Purpose                          |
| ------------------------ | ------------------------------- | -------------------------------- |
| `VITE_API_BASE_URL`      | `http://127.0.0.1:8000`         | Frontend API base URL (set on **Vercel** at build time) |
| `FAILSAFE_CORS_ORIGINS`  | (none)                          | Extra CORS origins for Render (comma-separated) |
| `FAILSAFE_PUBLIC_URL`    | (from request headers)          | Public API URL for chart links on **Render**      |
| `FAILSAFE_SECRET_KEY`    | dev secret in code              | JWT signing key (set on **Render**)              |
| `FAILSAFE_TOKEN_TTL_MINUTES` | `480`                       | Token lifetime in minutes        |

### Vercel + Render

1. **Vercel** → Environment Variables → `VITE_API_BASE_URL=https://failsafe-naix.onrender.com` (no trailing slash) → **Redeploy**
2. **Render** → redeploy after pulling latest backend (CORS allows `*.vercel.app`)
3. Optional on Render: `FAILSAFE_CORS_ORIGINS=https://your-custom-domain.com`

## API routes

| Method | Path                              | Auth | Description                    |
| ------ | --------------------------------- | ---- | ------------------------------ |
| POST   | `/auth/login`                     | No   | Faculty login                  |
| GET    | `/auth/me`                        | Yes  | Current user profile           |
| POST   | `/upload`                         | Yes  | Upload CSVs and retrain        |
| POST   | `/predict`                        | Yes  | Batch predictions + SHAP chart |
| GET    | `/dashboard`                      | Yes  | Summary metrics and charts     |
| GET    | `/faculty/analytics`              | Yes  | High-risk and feature stats    |
| GET    | `/students/{student_id}/explanation` | Yes | SHAP + interventions for one student |
| GET    | `/report`                         | Yes  | PDF risk report download       |
| GET    | `/charts/shap_summary.png`        | No   | Global SHAP summary image        |

Protected routes expect: `Authorization: Bearer <token>`

## Verification

From the project root:

```bash
python -m backend.models.train_model
python -m compileall backend
cd frontend
npm run lint
npm run build
```

Expected: model accuracy ~**90.4%** on the bundled 1,044 merged records; frontend build completes without errors.

## Troubleshooting

- **“Could not reach the FAILSAFE API”** — Start the backend on port 8000 before opening the frontend.
- **Upload rejected** — Filenames must be exactly `student-mat.csv` and `student-por.csv`.
- **Module not found (`backend`)** — Run Python commands from the project root, not from inside `backend/`.
- **Frontend build fails on Windows** — Run `npm run build` from `frontend/` in a normal terminal (not a restricted sandbox).
