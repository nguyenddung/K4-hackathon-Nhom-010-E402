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
| POST | `/candidates/{id}/rescreen` | Re-run the grounded CV-to-JD assessment |
| POST | `/cv/upload` | Parse, section-chunk, and locally embed a PDF/DOCX |
| POST | `/cv/{id}/analyze` | Retrieve evidence by rubric and analyze only those chunks with Gemini |
| GET | `/dashboard`, `/analytics`, `/audit` | Dashboard and audit data |

`GET /candidates` accepts `search`, `job_id`, `limit` (1–100), and `offset`. It returns `{ items, total, limit, offset }`.

## Implementation notes

- Passwords use `scrypt`; tokens are HMAC signed and expire after `TOKEN_TTL_MINUTES`.
- SQLite runs with WAL, foreign keys, transactions, indexes, and a non-destructive schema migration for existing local databases.
- Candidate creation and HR decisions add audit events in the same transaction as the mutation.
- Set `AI_PROVIDER=openai` or `AI_PROVIDER=gemini` to select the LLM for every assessment route. If the selected key/request fails, the legacy candidate workflow uses its deterministic local fallback.
- Before AI processing, the service rejects prompt-injection patterns and redacts PII, demographic attributes, address, age, and school identifiers. The model receives only this reduced, job-relevant text.
- Names, email addresses, CV text, and uploaded filenames are encrypted at rest. HMAC blind indexes support exact name/email search without decrypting database rows.
- PDF and DOCX are extracted in memory; password-protected/corrupt files and documents with too little readable text are rejected.

## Select OpenAI or Gemini

Configure both keys once, then switch the whole backend with `AI_PROVIDER`:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-3.5-flash

OPENAI_API_KEY=your-key
OPENAI_CHAT_MODEL=gpt-4o-mini
```

Use `AI_PROVIDER=openai` for OpenAI or `AI_PROVIDER=gemini` for Gemini, then
restart Uvicorn. `GET /health` reports the provider and model currently active.

## CV RAG

`LOCAL_EMBED_MODEL` defaults to the multilingual sentence-transformers model in
`.env.example`. The first upload may download the local embedding model.

Upload (this step does not call Gemini):

```powershell
curl.exe -X POST http://127.0.0.1:8000/cv/upload `
  -H "Authorization: Bearer $token" `
  -F "cv=@D:\CVs\candidate.pdf"
```

Analyze with a custom rubric:

```powershell
$body = @{
  top_k = 3
  rubric = @(
    @{
      id = "python"
      name = "Python"
      description = "Kinh nghiệm Python trong dự án production"
      weight = 60
    },
    @{
      id = "system_design"
      name = "System design"
      description = "Bằng chứng thiết kế hệ thống và quyết định kiến trúc"
      weight = 40
    }
  )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/cv/$cvId/analyze" `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body $body
```

The selected provider returns schema-validated JSON. Each criterion contains a verdict, score,
rationale, and exact evidence quotes tied to a retrieved `chunk_id` and section.
CV text, parsed fields, filenames, and chunks are encrypted at rest. Only the
retrieved chunks are redacted and sent to the selected provider.
