"""HTTP API for the V-AI Recruiter web client."""

import datetime
import hashlib
import json
import secrets
import sqlite3
import uuid
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from ai_service import candidate_assessment, cosine_sim, embed_text, load_assessment
from database import get_conn, init_db, log_audit


DEMO_ACCOUNTS = (
    ("demo@vairecruiter.local", "Demo@123", "Nguyen Minh Anh", "HR Manager"),
    ("hr@vairecruiter.local", "HR@123456", "Tran Thu Ha", "Recruiter"),
)
TOKENS: dict[str, dict[str, str]] = {}
security = HTTPBearer(auto_error=False)

app = FastAPI(title="V-AI Recruiter API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    email: str
    password: str


class JobRequest(BaseModel):
    title: str
    description: str


class CandidateRequest(BaseModel):
    job_id: str
    name: str
    cv_text: str


class DecisionRequest(BaseModel):
    decision: str
    note: str = ""


def password_hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def seed_demo_accounts() -> None:
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    for email, password, name, role in DEMO_ACCOUNTS:
        conn.execute(
            """
            INSERT OR IGNORE INTO users (id, email, password_hash, name, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), email, password_hash(password), name, role, datetime.datetime.utcnow().isoformat()),
        )
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_demo_accounts()


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict[str, str]:
    if credentials is None or credentials.credentials not in TOKENS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Phiên đăng nhập không hợp lệ.")
    return TOKENS[credentials.credentials]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login")
def login(payload: LoginRequest) -> dict[str, object]:
    conn = get_conn()
    user = conn.execute(
        "SELECT id, email, name, role, password_hash FROM users WHERE email = ?",
        (payload.email.strip().lower(),),
    ).fetchone()
    conn.close()
    if user is None or not secrets.compare_digest(user["password_hash"], password_hash(payload.password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email hoặc mật khẩu không đúng.")

    token = secrets.token_urlsafe(32)
    profile = {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]}
    TOKENS[token] = profile
    return {"access_token": token, "token_type": "bearer", "user": profile}


@app.get("/dashboard")
def dashboard(user: Annotated[dict[str, str], Depends(current_user)]) -> dict[str, object]:
    conn = get_conn()
    jobs = conn.execute("SELECT COUNT(*) AS total FROM jobs").fetchone()["total"]
    candidates = conn.execute("SELECT COUNT(*) AS total FROM candidates").fetchone()["total"]
    decisions = conn.execute("SELECT decision, COUNT(*) AS total FROM decisions GROUP BY decision").fetchall()
    recent_candidates = conn.execute(
        """
        SELECT c.name, c.score, c.created_at, j.title AS job_title
        FROM candidates c JOIN jobs j ON c.job_id = j.id
        ORDER BY c.created_at DESC LIMIT 5
        """
    ).fetchall()
    conn.close()
    return {
        "user": user,
        "metrics": {"open_jobs": jobs, "screened_candidates": candidates, "decisions": {item["decision"]: item["total"] for item in decisions}},
        "recent_candidates": [dict(item) for item in recent_candidates],
    }


@app.get("/jobs")
def list_jobs(user: Annotated[dict[str, str], Depends(current_user)]) -> list[dict[str, object]]:
    conn = get_conn()
    jobs = conn.execute(
        """
        SELECT j.id, j.title, j.description, j.created_at, COUNT(c.id) AS candidate_count
        FROM jobs j LEFT JOIN candidates c ON c.job_id = j.id
        GROUP BY j.id ORDER BY j.created_at DESC
        """
    ).fetchall()
    conn.close()
    return [dict(job) for job in jobs]


@app.post("/jobs", status_code=status.HTTP_201_CREATED)
def create_job(payload: JobRequest, user: Annotated[dict[str, str], Depends(current_user)]) -> dict[str, object]:
    title, description = payload.title.strip(), payload.description.strip()
    if not title or not description:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Tên vị trí và JD là bắt buộc.")

    job = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "created_at": datetime.datetime.utcnow().isoformat(),
    }
    conn = get_conn()
    conn.execute(
        "INSERT INTO jobs (id, title, description, embedding, created_at) VALUES (?,?,?,?,?)",
        (job["id"], title, description, json.dumps(embed_text(description)), job["created_at"]),
    )
    conn.commit()
    conn.close()
    log_audit(job["id"], "create_job", f"Tạo job '{title}' bởi {user['email']}")
    return {**job, "candidate_count": 0}


@app.get("/candidates")
def list_candidates(
    user: Annotated[dict[str, str], Depends(current_user)], job_id: str | None = None
) -> list[dict[str, object]]:
    conn = get_conn()
    query = """
        SELECT c.id, c.job_id, c.name, c.score, c.reasoning, c.created_at, j.title AS job_title,
               d.decision, d.note, d.created_at AS decision_created_at
        FROM candidates c
        JOIN jobs j ON c.job_id = j.id
        LEFT JOIN decisions d ON d.id = (
            SELECT id FROM decisions WHERE candidate_id = c.id ORDER BY created_at DESC LIMIT 1
        )
    """
    parameters: tuple[str, ...] = ()
    if job_id:
        query += " WHERE c.job_id = ?"
        parameters = (job_id,)
    query += " ORDER BY c.created_at DESC"
    candidates = conn.execute(query, parameters).fetchall()
    conn.close()
    results = []
    for candidate in candidates:
        result = dict(candidate)
        result["assessment"] = load_assessment(result.pop("reasoning"))
        results.append(result)
    return results


@app.post("/candidates", status_code=status.HTTP_201_CREATED)
def screen_candidate(
    payload: CandidateRequest, user: Annotated[dict[str, str], Depends(current_user)]
) -> dict[str, object]:
    name, cv_text = payload.name.strip(), payload.cv_text.strip()
    if not name or not cv_text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Tên ứng viên và nội dung CV là bắt buộc.")

    conn = get_conn()
    job = conn.execute("SELECT title, description, embedding FROM jobs WHERE id = ?", (payload.job_id,)).fetchone()
    if job is None:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy job đã chọn.")

    candidate_embedding = embed_text(cv_text)
    score = cosine_sim(json.loads(job["embedding"]), candidate_embedding)
    assessment = candidate_assessment(job["description"], cv_text, score)
    candidate = {
        "id": str(uuid.uuid4()),
        "job_id": payload.job_id,
        "name": name,
        "score": score,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "job_title": job["title"],
        "assessment": assessment,
        "decision": None,
        "note": None,
    }
    conn.execute(
        """INSERT INTO candidates (id, job_id, name, cv_text, embedding, score, reasoning, created_at)
           VALUES (?,?,?,?,?,?,?,?)""",
        (candidate["id"], payload.job_id, name, cv_text, json.dumps(candidate_embedding), score,
         json.dumps(assessment, ensure_ascii=False), candidate["created_at"]),
    )
    conn.commit()
    conn.close()
    log_audit(candidate["id"], "screen_cv", f"Chấm CV '{name}' cho job {payload.job_id[:8]} bởi {user['email']}")
    return candidate


@app.put("/candidates/{candidate_id}/decision")
def save_decision(
    candidate_id: str, payload: DecisionRequest, user: Annotated[dict[str, str], Depends(current_user)]
) -> dict[str, str]:
    valid_decisions = {"Pass", "Hold", "Reject"}
    if payload.decision not in valid_decisions:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Quyết định không hợp lệ.")

    conn = get_conn()
    candidate = conn.execute("SELECT id FROM candidates WHERE id = ?", (candidate_id,)).fetchone()
    if candidate is None:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy ứng viên.")
    latest = conn.execute(
        "SELECT id, decision FROM decisions WHERE candidate_id = ? ORDER BY created_at DESC LIMIT 1", (candidate_id,)
    ).fetchone()
    saved_at = datetime.datetime.utcnow().isoformat()
    if latest:
        conn.execute("UPDATE decisions SET decision = ?, note = ?, created_at = ? WHERE id = ?", (payload.decision, payload.note.strip(), saved_at, latest["id"]))
        action = "update_hr_decision"
    else:
        conn.execute(
            "INSERT INTO decisions (id, candidate_id, decision, note, created_at) VALUES (?,?,?,?,?)",
            (str(uuid.uuid4()), candidate_id, payload.decision, payload.note.strip(), saved_at),
        )
        action = "hr_decision"
    conn.commit()
    conn.close()
    log_audit(candidate_id, action, f"{payload.decision} bởi {user['email']}")
    return {"decision": payload.decision, "note": payload.note.strip(), "created_at": saved_at}


@app.get("/analytics")
def analytics(user: Annotated[dict[str, str], Depends(current_user)]) -> dict[str, object]:
    conn = get_conn()
    scores = [row["score"] for row in conn.execute("SELECT score FROM candidates").fetchall()]
    decisions = conn.execute("SELECT decision, COUNT(*) AS total FROM decisions GROUP BY decision").fetchall()
    conn.close()
    return {
        "candidate_count": len(scores),
        "average_score": sum(scores) / len(scores) if scores else None,
        "highest_score": max(scores) if scores else None,
        "lowest_score": min(scores) if scores else None,
        "decision_distribution": {row["decision"]: row["total"] for row in decisions},
    }


@app.get("/audit")
def audit_log(user: Annotated[dict[str, str], Depends(current_user)]) -> list[dict[str, str]]:
    conn = get_conn()
    logs = conn.execute("SELECT id, entity_id, action, detail, created_at FROM audit_log ORDER BY created_at DESC LIMIT 100").fetchall()
    conn.close()
    return [dict(log) for log in logs]