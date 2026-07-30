# V-AI Recruiter API

FastAPI backend for jobs, candidates, screening assessments, decisions, and audit history.

## Run

```powershell
Copy-Item .env.example .env
# Set SECRET_KEY in .env before deploying.
python -m pip install -r requirements.txt
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000/docs` in development. The sample users are `demo@vairecruiter.local` / `Demo@123` and `hr@vairecruiter.local` / `HR@123456`.

## API contract

All routes except `/health` and `/auth/login` need `Authorization: Bearer <access_token>`.

| Method | Route | Purpose |
| --- | --- | --- |
| POST | `/auth/login` | Authenticate and receive a signed, expiring token |
| POST | `/auth/register` | Register an HR Manager/Recruiter account and receive a token |
| GET | `/auth/me` | Current user profile |
| GET, POST | `/jobs` | List and create job openings |
| GET, POST | `/candidates` | Paginated candidate list and protected text-CV screening |
| POST | `/candidates/upload` | Upload PDF/DOCX, extract text, run protected AI screening |
| GET, PATCH | `/candidates/{id}` | Candidate detail and profile update |
| PUT | `/candidates/{id}/decision` | Save Pass/Hold/Reject decision |
| GET | `/dashboard`, `/analytics`, `/audit` | Dashboard and audit data |

`GET /candidates` accepts `search`, `job_id`, `limit` (1–100), and `offset`. It returns `{ items, total, limit, offset }`.

## Implementation notes

- Passwords use `scrypt`; tokens are HMAC signed and expire after `TOKEN_TTL_MINUTES`.
- SQLite runs with WAL, foreign keys, transactions, indexes, and a non-destructive schema migration for existing local databases.
- Candidate creation and HR decisions add audit events in the same transaction as the mutation.
- Set `OPENAI_API_KEY` to enable the assessment integration. Its deterministic local fallback keeps demo scores stable without a key.
- Before AI processing, the service rejects prompt-injection patterns and redacts PII, demographic attributes, address, age, and school identifiers. The model receives only this reduced, job-relevant text.
- Names, email addresses, CV text, and uploaded filenames are encrypted at rest. HMAC blind indexes support exact name/email search without decrypting database rows.
- PDF and DOCX are extracted in memory; password-protected/corrupt files and documents with too little readable text are rejected.
