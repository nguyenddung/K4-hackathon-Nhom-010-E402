"""Domain states, transition rules, and role guards for TalentScreen AI."""

from __future__ import annotations

from enum import StrEnum
from typing import Iterable


class Role(StrEnum):
    HR = "HR"
    CANDIDATE = "CANDIDATE"
    AGENT = "AGENT"
    INTERVIEWER = "INTERVIEWER"


class JobStatus(StrEnum):
    DRAFT = "DRAFT_JOB"
    RUBRIC_REVIEW = "RUBRIC_REVIEW"
    APPROVED = "JOB_APPROVED"
    PUBLISHED = "JOB_PUBLISHED"
    CLOSED = "JOB_CLOSED"


class ApplicationStatus(StrEnum):
    SUBMITTED = "APPLICATION_SUBMITTED"
    QUEUED = "CV_QUEUED"
    PROCESSING = "CV_PROCESSING"
    ANALYZED = "CV_ANALYZED"
    HR_REVIEW_PENDING = "HR_REVIEW_PENDING"
    NEED_MORE_INFORMATION = "NEED_MORE_INFORMATION"
    SHORTLISTED = "SHORTLISTED"
    TALENT_POOL = "TALENT_POOL"
    NOT_PROCEEDING = "NOT_PROCEEDING"
    INTERVIEW_INVITED = "INTERVIEW_INVITED"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    INTERVIEW_COMPLETED = "INTERVIEW_COMPLETED"
    SCORECARD_PENDING = "SCORECARD_PENDING"
    INTERVIEWER_SUBMITTED = "INTERVIEWER_SUBMITTED"
    AGENT_SUMMARIZED = "AGENT_SUMMARIZED"
    NEXT_ROUND = "NEXT_ROUND"
    ASSESSMENT_REQUIRED = "ASSESSMENT_REQUIRED"
    OFFER_PENDING = "OFFER_PENDING"
    OFFER_ACCEPTED = "OFFER_ACCEPTED"
    OFFER_DECLINED = "OFFER_DECLINED"
    OFFER_EXPIRED = "OFFER_EXPIRED"
    HIRED = "HIRED"
    ONBOARDING = "ONBOARDING"
    CLOSED = "CLOSED"


class FeedbackStatus(StrEnum):
    NONE = "NONE"
    GENERATED = "FEEDBACK_GENERATED"
    HR_APPROVED = "HR_APPROVED_FEEDBACK"
    SENT = "FEEDBACK_SENT"


JOB_TRANSITIONS: dict[JobStatus, set[JobStatus]] = {
    JobStatus.DRAFT: {JobStatus.RUBRIC_REVIEW},
    JobStatus.RUBRIC_REVIEW: {JobStatus.DRAFT, JobStatus.APPROVED},
    JobStatus.APPROVED: {JobStatus.RUBRIC_REVIEW, JobStatus.PUBLISHED},
    JobStatus.PUBLISHED: {JobStatus.CLOSED},
    JobStatus.CLOSED: set(),
}


APPLICATION_TRANSITIONS: dict[ApplicationStatus, set[ApplicationStatus]] = {
    ApplicationStatus.SUBMITTED: {ApplicationStatus.QUEUED},
    ApplicationStatus.QUEUED: {ApplicationStatus.PROCESSING},
    ApplicationStatus.PROCESSING: {ApplicationStatus.ANALYZED, ApplicationStatus.QUEUED},
    ApplicationStatus.ANALYZED: {ApplicationStatus.HR_REVIEW_PENDING},
    ApplicationStatus.HR_REVIEW_PENDING: {
        ApplicationStatus.NEED_MORE_INFORMATION,
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.TALENT_POOL,
        ApplicationStatus.NOT_PROCEEDING,
    },
    ApplicationStatus.NEED_MORE_INFORMATION: {ApplicationStatus.SUBMITTED, ApplicationStatus.NOT_PROCEEDING},
    ApplicationStatus.SHORTLISTED: {ApplicationStatus.INTERVIEW_INVITED, ApplicationStatus.TALENT_POOL, ApplicationStatus.NOT_PROCEEDING},
    ApplicationStatus.INTERVIEW_INVITED: {ApplicationStatus.INTERVIEW_SCHEDULED, ApplicationStatus.NOT_PROCEEDING},
    ApplicationStatus.INTERVIEW_SCHEDULED: {ApplicationStatus.INTERVIEW_COMPLETED},
    ApplicationStatus.INTERVIEW_COMPLETED: {ApplicationStatus.SCORECARD_PENDING},
    ApplicationStatus.SCORECARD_PENDING: {ApplicationStatus.INTERVIEWER_SUBMITTED},
    ApplicationStatus.INTERVIEWER_SUBMITTED: {ApplicationStatus.AGENT_SUMMARIZED},
    ApplicationStatus.AGENT_SUMMARIZED: {
        ApplicationStatus.NEXT_ROUND,
        ApplicationStatus.ASSESSMENT_REQUIRED,
        ApplicationStatus.OFFER_PENDING,
        ApplicationStatus.TALENT_POOL,
        ApplicationStatus.NOT_PROCEEDING,
    },
    ApplicationStatus.NEXT_ROUND: {ApplicationStatus.INTERVIEW_INVITED},
    ApplicationStatus.ASSESSMENT_REQUIRED: {
        ApplicationStatus.OFFER_PENDING,
        ApplicationStatus.NEXT_ROUND,
        ApplicationStatus.NOT_PROCEEDING,
    },
    ApplicationStatus.OFFER_PENDING: {
        ApplicationStatus.OFFER_ACCEPTED,
        ApplicationStatus.OFFER_DECLINED,
        ApplicationStatus.OFFER_EXPIRED,
    },
    ApplicationStatus.OFFER_ACCEPTED: {ApplicationStatus.HIRED},
    ApplicationStatus.HIRED: {ApplicationStatus.ONBOARDING},
    ApplicationStatus.ONBOARDING: {ApplicationStatus.CLOSED},
    ApplicationStatus.OFFER_DECLINED: {ApplicationStatus.CLOSED},
    ApplicationStatus.OFFER_EXPIRED: {ApplicationStatus.CLOSED},
    ApplicationStatus.TALENT_POOL: {ApplicationStatus.CLOSED},
    ApplicationStatus.NOT_PROCEEDING: {ApplicationStatus.CLOSED},
    ApplicationStatus.CLOSED: set(),
}


JOB_STATUS_ALIASES = {
    "DRAFT": JobStatus.DRAFT,
    "APPROVED": JobStatus.APPROVED,
    "PUBLISHED": JobStatus.PUBLISHED,
}

APPLICATION_STATUS_ALIASES = {
    "SUBMITTED": ApplicationStatus.SUBMITTED,
    "CV_ANALYZED": ApplicationStatus.ANALYZED,
    "REJECTED": ApplicationStatus.NOT_PROCEEDING,
}


class AuthorizationError(PermissionError):
    """Raised when a role attempts an operation it is not allowed to perform."""


class InvalidTransitionError(ValueError):
    """Raised when a state transition violates the domain state machine."""


def normalize_job_status(value: str | JobStatus) -> JobStatus:
    if isinstance(value, JobStatus):
        return value
    if value in JOB_STATUS_ALIASES:
        return JOB_STATUS_ALIASES[value]
    return JobStatus(value)


def normalize_application_status(value: str | ApplicationStatus) -> ApplicationStatus:
    if isinstance(value, ApplicationStatus):
        return value
    if value in APPLICATION_STATUS_ALIASES:
        return APPLICATION_STATUS_ALIASES[value]
    return ApplicationStatus(value)


def require_role(role: str | Role, allowed: Iterable[str | Role]) -> None:
    actual = Role(role)
    allowed_roles = {Role(item) for item in allowed}
    if actual not in allowed_roles:
        expected = ", ".join(sorted(item.value for item in allowed_roles))
        raise AuthorizationError(f"Role {actual.value} không có quyền thực hiện thao tác này; yêu cầu: {expected}.")


def validate_job_transition(current: str | JobStatus, target: str | JobStatus) -> tuple[JobStatus, JobStatus]:
    current_state = normalize_job_status(current)
    target_state = normalize_job_status(target)
    if target_state not in JOB_TRANSITIONS[current_state]:
        raise InvalidTransitionError(f"Không thể chuyển Job từ {current_state.value} sang {target_state.value}.")
    return current_state, target_state


def validate_application_transition(
    current: str | ApplicationStatus,
    target: str | ApplicationStatus,
) -> tuple[ApplicationStatus, ApplicationStatus]:
    current_state = normalize_application_status(current)
    target_state = normalize_application_status(target)
    if target_state not in APPLICATION_TRANSITIONS[current_state]:
        raise InvalidTransitionError(
            f"Không thể chuyển hồ sơ từ {current_state.value} sang {target_state.value}."
        )
    return current_state, target_state
