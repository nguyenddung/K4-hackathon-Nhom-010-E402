"""Production-oriented REST API for the recruiting workspace."""

import base64
import hashlib
import hmac
import json
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, field_validator

from ai_service import candidate_assessment, cosine_sim, embed_text, load_assessment
from config import APP_ENV, CORS_ORIGINS, SECRET_KEY, TOKEN_TTL_MINUTES
from database import get_conn, init_db, log_audit, now, transaction
from document_service import DocumentError, extract_cv_text
from security_service import SecurityViolation, blind_index, decrypt, encrypt, redact_for_ai

DEMO_ACCOUNTS = (("demo@vairecruiter.local", "Demo@123", "Nguyen Minh Anh", "HR Manager"), ("hr@vairecruiter.local", "HR@123456", "Tran Thu Ha", "Recruiter"))
security = HTTPBearer(auto_error=False)

app = FastAPI(title="V-AI Recruiter API", version="2.0.0", docs_url="/docs" if APP_ENV != "production" else None)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Authorization", "Content-Type"])


class ApiModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class LoginRequest(ApiModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=256)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Invalid email address")
        return value


class RegisterRequest(LoginRequest):
    name: str = Field(min_length=2, max_length=160)
    role: Literal["HR Manager", "Recruiter"] = "Recruiter"


class JobRequest(ApiModel):
    title: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=20, max_length=20_000)


class CandidateRequest(ApiModel):
    job_id: str = Field(min_length=36, max_length=36)
    name: str = Field(min_length=2, max_length=160)
    email: str | None = Field(default=None, max_length=254)
    cv_text: str = Field(min_length=30, max_length=50_000)


class CandidateUpdate(ApiModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    email: str | None = Field(default=None, max_length=254)


class DecisionRequest(ApiModel):
    decision: Literal["Pass", "Hold", "Reject"]
    note: str = Field(default="", max_length=2_000)


def api_error(code: int, message: str) -> HTTPException:
    return HTTPException(status_code=code, detail=message)


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt$16384${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, n, salt, expected = stored.split("$")
        if scheme != "scrypt": return False
        actual = hashlib.scrypt(password.encode(), salt=base64.urlsafe_b64decode(salt), n=int(n), r=8, p=1)
        return hmac.compare_digest(actual, base64.urlsafe_b64decode(expected))
    except (ValueError, TypeError):
        return False


def _b64(value: bytes) -> str: return base64.urlsafe_b64encode(value).rstrip(b"=").decode()
def _unb64(value: str) -> bytes: return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def issue_token(user: dict[str, str]) -> str:
    payload = {"sub": user["id"], "email": user["email"], "exp": int((datetime.now(UTC) + timedelta(minutes=TOKEN_TTL_MINUTES)).timestamp())}
    body = _b64(json.dumps(payload, separators=(",", ":")).encode())
    signature = _b64(hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest())
    return f"{body}.{signature}"


def current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]) -> dict[str, str]:
    if credentials is None or credentials.scheme.lower() != "bearer": raise api_error(401, "Authentication required")
    try:
        body, supplied_signature = credentials.credentials.split(".")
        expected_signature = _b64(hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest())
        payload = json.loads(_unb64(body))
        if not hmac.compare_digest(supplied_signature, expected_signature) or payload["exp"] <= int(datetime.now(UTC).timestamp()): raise ValueError
    except (ValueError, KeyError, json.JSONDecodeError):
        raise api_error(401, "Invalid or expired token")
    conn = get_conn()
    row = conn.execute("SELECT id, email, name, role FROM users WHERE id = ?", (payload["sub"],)).fetchone(); conn.close()
    if row is None: raise api_error(401, "User no longer exists")
    return dict(row)


def candidate_dict(row: object) -> dict[str, object]:
    item = dict(row)
    item["assessment"] = load_assessment(item.pop("reasoning"))
    item["name"] = decrypt(item.pop("encrypted_name", None)) or item["name"]
    item["email"] = decrypt(item.pop("encrypted_email", None)) or item.get("email")
    item["cv_filename"] = decrypt(item.pop("encrypted_cv_filename", None))
    item.pop("encrypted_cv_text", None)
    item.pop("name_blind_index", None)
    item.pop("email_blind_index", None)
    return item


def seed_demo_accounts() -> None:
    with transaction() as conn:
        for email, password, name, role in DEMO_ACCOUNTS:
            existing = conn.execute("SELECT password_hash FROM users WHERE email = ?", (email,)).fetchone()
            if existing is None:
                conn.execute("INSERT INTO users (id,email,password_hash,name,role,created_at) VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), email, hash_password(password), name, role, now()))
            elif not existing["password_hash"].startswith("scrypt$"):
                # One-time upgrade for the bundled development accounts.
                conn.execute("UPDATE users SET password_hash=?,updated_at=? WHERE email=?", (hash_password(password), now(), email))


@app.on_event("startup")
def startup() -> None:
    init_db(); seed_demo_accounts()


@app.exception_handler(HTTPException)
async def http_error(_: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health")
def health() -> dict[str, str]: return {"status": "ok", "version": app.version}


@app.post("/auth/login")
def login(payload: LoginRequest) -> dict[str, object]:
    conn = get_conn(); row = conn.execute("SELECT id,email,name,role,password_hash FROM users WHERE email = ?", (payload.email,)).fetchone(); conn.close()
    if row is None or not verify_password(payload.password, row["password_hash"]): raise api_error(401, "Incorrect email or password")
    profile = {key: row[key] for key in ("id", "email", "name", "role")}
    return {"access_token": issue_token(profile), "token_type": "bearer", "expires_in": TOKEN_TTL_MINUTES * 60, "user": profile}


@app.post("/auth/register", status_code=201)
def register(payload: RegisterRequest) -> dict[str, object]:
    user = {"id": str(uuid.uuid4()), "email": payload.email, "name": payload.name, "role": payload.role}
    try:
        with transaction() as conn:
            conn.execute(
                "INSERT INTO users (id,email,password_hash,name,role,created_at) VALUES (?,?,?,?,?,?)",
                (user["id"], user["email"], hash_password(payload.password), user["name"], user["role"], now()),
            )
            log_audit(conn, user["id"], "user.registered", f"Registered HR account: {user['role']}", user["id"])
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise api_error(409, "Email already registered")
        raise
    return {"access_token": issue_token(user), "token_type": "bearer", "expires_in": TOKEN_TTL_MINUTES * 60, "user": user}


@app.get("/auth/me")
def me(user: Annotated[dict[str, str], Depends(current_user)]) -> dict[str, str]: return user


@app.get("/dashboard")
def dashboard(user: Annotated[dict[str, str], Depends(current_user)]) -> dict[str, object]:
    conn = get_conn()
    jobs = conn.execute("SELECT COUNT(*) total FROM jobs WHERE status = 'open'").fetchone()["total"]
    candidates = conn.execute("SELECT COUNT(*) total FROM candidates").fetchone()["total"]
    decisions = conn.execute("SELECT decision, COUNT(*) total FROM decisions GROUP BY decision").fetchall()
    conn.close()
    return {"user": user, "metrics": {"open_jobs": jobs, "screened_candidates": candidates, "decisions": {item["decision"]: item["total"] for item in decisions}}}


@app.get("/jobs")
def list_jobs(user: Annotated[dict[str, str], Depends(current_user)], status_filter: Literal["open", "closed"] | None = Query(None, alias="status")) -> list[dict[str, object]]:
    sql = "SELECT j.id,j.title,j.description,j.status,j.created_at,j.updated_at,COUNT(c.id) candidate_count FROM jobs j LEFT JOIN candidates c ON c.job_id=j.id"
    params: tuple[str, ...] = ()
    if status_filter: sql += " WHERE j.status=?"; params = (status_filter,)
    sql += " GROUP BY j.id ORDER BY j.created_at DESC"
    conn = get_conn(); rows = conn.execute(sql, params).fetchall(); conn.close(); return [dict(row) for row in rows]


@app.post("/jobs", status_code=201)
def create_job(payload: JobRequest, user: Annotated[dict[str, str], Depends(current_user)]) -> dict[str, object]:
    job = {"id": str(uuid.uuid4()), "title": payload.title, "description": payload.description, "status": "open", "created_at": now()}
    with transaction() as conn:
        conn.execute("INSERT INTO jobs (id,title,description,embedding,status,created_at) VALUES (?,?,?,?,?,?)", (job["id"], job["title"], job["description"], json.dumps(embed_text(payload.description)), job["status"], job["created_at"]))
        log_audit(conn, job["id"], "job.created", f"Created job: {job['title']}", user["id"])
    return {**job, "candidate_count": 0}


@app.get("/candidates")
def list_candidates(user: Annotated[dict[str, str], Depends(current_user)], job_id: str | None = None, search: str | None = Query(None, max_length=120), limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)) -> dict[str, object]:
    clauses, params = [], []
    if job_id: clauses.append("c.job_id = ?"); params.append(job_id)
    if search:
        # PII remains encrypted: candidate identity search uses deterministic blind indexes.
        clauses.append("(c.name_blind_index = ? OR c.email_blind_index = ? OR j.title LIKE ?)")
        params.extend([blind_index(search), blind_index(search), f"%{search}%"])
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    select = "SELECT c.id,c.job_id,c.name,c.email,c.encrypted_name,c.encrypted_email,c.encrypted_cv_text,c.encrypted_cv_filename,c.name_blind_index,c.email_blind_index,c.security_status,c.redaction_count,c.score,c.reasoning,c.created_at,c.updated_at,j.title job_title,d.decision,d.note,d.updated_at decision_updated_at FROM candidates c JOIN jobs j ON j.id=c.job_id LEFT JOIN decisions d ON d.candidate_id=c.id"
    conn = get_conn(); total = conn.execute(f"SELECT COUNT(*) total FROM candidates c JOIN jobs j ON j.id=c.job_id{where}", params).fetchone()["total"]
    rows = conn.execute(f"{select}{where} ORDER BY c.created_at DESC LIMIT ? OFFSET ?", [*params, limit, offset]).fetchall(); conn.close()
    return {"items": [candidate_dict(row) for row in rows], "total": total, "limit": limit, "offset": offset}


@app.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str, user: Annotated[dict[str, str], Depends(current_user)]) -> dict[str, object]:
    conn = get_conn(); row = conn.execute("SELECT c.id,c.job_id,c.name,c.email,c.encrypted_name,c.encrypted_email,c.encrypted_cv_text,c.encrypted_cv_filename,c.name_blind_index,c.email_blind_index,c.security_status,c.redaction_count,c.score,c.reasoning,c.created_at,c.updated_at,j.title job_title,d.decision,d.note,d.updated_at decision_updated_at FROM candidates c JOIN jobs j ON j.id=c.job_id LEFT JOIN decisions d ON d.candidate_id=c.id WHERE c.id=?", (candidate_id,)).fetchone(); conn.close()
    if row is None: raise api_error(404, "Candidate not found")
    return candidate_dict(row)


@app.post("/candidates", status_code=201)
def create_candidate(payload: CandidateRequest, user: Annotated[dict[str, str], Depends(current_user)]) -> dict[str, object]:
    conn = get_conn(); job = conn.execute("SELECT id,title,description,embedding,status FROM jobs WHERE id=?", (payload.job_id,)).fetchone(); conn.close()
    if job is None: raise api_error(404, "Job not found")
    if job["status"] != "open": raise api_error(409, "Cannot add candidates to a closed job")
    try:
        safe_cv = redact_for_ai(payload.cv_text)
        safe_jd = redact_for_ai(job["description"])
    except SecurityViolation as exc:
        raise api_error(422, str(exc))
    embedding = embed_text(safe_cv.text); score = max(0.0, min(1.0, cosine_sim(json.loads(job["embedding"]), embedding))); assessment = candidate_assessment(safe_jd.text, safe_cv.text, score)
    candidate = {"id": str(uuid.uuid4()), "job_id": payload.job_id, "name": payload.name, "email": payload.email, "score": score, "reasoning": json.dumps(assessment, ensure_ascii=False), "created_at": now(), "security_status": "protected", "redaction_count": safe_cv.redactions}
    with transaction() as write_conn:
        write_conn.execute("""INSERT INTO candidates (id,job_id,name,email,cv_text,embedding,score,reasoning,created_at,encrypted_name,encrypted_email,encrypted_cv_text,name_blind_index,email_blind_index,security_status,redaction_count)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (candidate["id"], candidate["job_id"], f"Candidate {candidate['id'][:8]}", None, "[ENCRYPTED]", json.dumps(embedding), candidate["score"], candidate["reasoning"], candidate["created_at"], encrypt(candidate["name"]), encrypt(candidate["email"]) if candidate["email"] else None, encrypt(payload.cv_text), blind_index(candidate["name"]), blind_index(candidate["email"]) if candidate["email"] else None, candidate["security_status"], candidate["redaction_count"]))
        log_audit(write_conn, candidate["id"], "candidate.created", "Created protected candidate record", user["id"])
    return {**candidate, "job_title": job["title"], "decision": None, "note": None, "assessment": assessment}


@app.patch("/candidates/{candidate_id}")
def update_candidate(candidate_id: str, payload: CandidateUpdate, user: Annotated[dict[str, str], Depends(current_user)]) -> dict[str, object]:
    changes = payload.model_dump(exclude_unset=True)
    if not changes: raise api_error(422, "Provide at least one field to update")
    with transaction() as conn:
        existing = conn.execute("SELECT id FROM candidates WHERE id=?", (candidate_id,)).fetchone()
        if existing is None: raise api_error(404, "Candidate not found")
        fields, values = [], []
        if "name" in changes:
            fields.extend(["encrypted_name=?", "name_blind_index=?"]); values.extend([encrypt(changes["name"]), blind_index(changes["name"])])
        if "email" in changes:
            fields.extend(["encrypted_email=?", "email_blind_index=?"]); values.extend([encrypt(changes["email"]) if changes["email"] else None, blind_index(changes["email"]) if changes["email"] else None])
        values.extend([now(), candidate_id])
        conn.execute(f"UPDATE candidates SET {','.join(fields)},updated_at=? WHERE id=?", values)
        log_audit(conn, candidate_id, "candidate.updated", "Updated candidate profile", user["id"])
    return get_candidate(candidate_id, user)


@app.post("/candidates/upload", status_code=201)
async def upload_candidate_cv(
    user: Annotated[dict[str, str], Depends(current_user)],
    job_id: Annotated[str, Form(min_length=36, max_length=36)],
    name: Annotated[str, Form(min_length=2, max_length=160)],
    email: Annotated[str | None, Form(max_length=254)] = None,
    cv: UploadFile = File(...),
) -> dict[str, object]:
    """Upload a PDF/DOCX, extract it in memory, then run the protected screening flow."""
    try:
        text = extract_cv_text(cv.filename or "", cv.content_type, await cv.read())
        result = create_candidate(CandidateRequest(job_id=job_id, name=name, email=email, cv_text=text), user)
    except DocumentError as exc:
        raise api_error(422, str(exc))
    finally:
        await cv.close()
    with transaction() as conn:
        conn.execute("UPDATE candidates SET encrypted_cv_filename=? WHERE id=?", (encrypt(cv.filename or "cv"), result["id"]))
        log_audit(conn, result["id"], "candidate.cv_uploaded", "Stored encrypted CV upload", user["id"])
    result["cv_filename"] = cv.filename
    return result


@app.put("/candidates/{candidate_id}/decision")
def save_decision(candidate_id: str, payload: DecisionRequest, user: Annotated[dict[str, str], Depends(current_user)]) -> dict[str, str]:
    saved_at = now()
    with transaction() as conn:
        if conn.execute("SELECT id FROM candidates WHERE id=?", (candidate_id,)).fetchone() is None: raise api_error(404, "Candidate not found")
        existing = conn.execute("SELECT id FROM decisions WHERE candidate_id=? ORDER BY created_at DESC LIMIT 1", (candidate_id,)).fetchone()
        if existing:
            conn.execute("UPDATE decisions SET decision=?,note=?,updated_at=? WHERE id=?", (payload.decision, payload.note, saved_at, existing["id"]))
        else:
            conn.execute("INSERT INTO decisions (id,candidate_id,decision,note,created_at,updated_at) VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), candidate_id, payload.decision, payload.note, saved_at, saved_at))
        log_audit(conn, candidate_id, "candidate.decision_saved", f"Decision: {payload.decision}", user["id"])
    return {"decision": payload.decision, "note": payload.note, "updated_at": saved_at}


@app.get("/analytics")
def analytics(user: Annotated[dict[str, str], Depends(current_user)]) -> dict[str, object]:
    conn = get_conn(); row = conn.execute("SELECT COUNT(*) candidate_count, AVG(score) average_score, MAX(score) highest_score, MIN(score) lowest_score FROM candidates").fetchone(); decisions = conn.execute("SELECT decision,COUNT(*) total FROM decisions GROUP BY decision").fetchall(); conn.close()
    return {**dict(row), "decision_distribution": {item["decision"]: item["total"] for item in decisions}}


@app.get("/audit")
def audit_log(user: Annotated[dict[str, str], Depends(current_user)], limit: int = Query(100, ge=1, le=200)) -> list[dict[str, object]]:
    conn = get_conn(); rows = conn.execute("SELECT id,entity_id,action,detail,actor_id,created_at FROM audit_log ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall(); conn.close(); return [dict(row) for row in rows]
