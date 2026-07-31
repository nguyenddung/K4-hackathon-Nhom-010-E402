"""Read-only diagnostic for the local CV upload and AI analysis flow."""

import json

from config import AI_PROVIDER
from database import get_conn
from llm_client import active_model_name
from security_service import decrypt


conn = get_conn()
rows = conn.execute(
    """SELECT id, encrypted_cv_text, reasoning, redaction_count, created_at
       FROM candidates ORDER BY created_at DESC LIMIT 10"""
).fetchall()

print("configured", {"provider": AI_PROVIDER, "model": active_model_name()})
print("candidate_count_checked", len(rows))
for row in rows:
    assessment = json.loads(row["reasoning"] or "{}")
    print(
        {
            "id": row["id"][:8],
            "decrypted_cv_chars": len(decrypt(row["encrypted_cv_text"]) or ""),
            "redaction_count": row["redaction_count"],
            "analysis_mode": assessment.get("analysis_mode"),
            "provider": assessment.get("provider"),
            "model": assessment.get("model"),
            "fallback_reason": str(assessment.get("fallback_reason", ""))[:200],
            "evidence_count": len(assessment.get("evidence", [])),
            "created_at": row["created_at"],
        }
    )

print("audit")
for row in conn.execute(
    """SELECT entity_id, action, detail, created_at
       FROM audit_log
       WHERE action IN (
         'candidate.created', 'candidate.cv_uploaded',
         'cv.rag_uploaded', 'cv.rag_analyzed'
       )
       ORDER BY created_at DESC LIMIT 20"""
).fetchall():
    print(dict(row))

print("rag_documents", conn.execute("SELECT COUNT(*) FROM cv_documents").fetchone()[0])
print("rag_chunks", conn.execute("SELECT COUNT(*) FROM cv_chunks").fetchone()[0])
conn.close()
