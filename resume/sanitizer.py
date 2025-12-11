"""Sanitization helpers for resume data and PDF-safe text.

This module converts raw mappings into typed DTOs (Pydantic models) while
sanitizing strings for PDF rendering.
"""
import calendar
from typing import Any
from resume.repository import HeaderSchema, RoleSchema, ResumeSchema, EmploymentType


def safe_text(text: Any):
    # robust low-level replacer; accept non-str and None
    if text is None:
        return ''
    s = str(text)
    return s.replace("\u2013", "-").replace("\u2014", "-").replace("\u2019", "'")


def sanitize_value(v: Any) -> str:
    """Convert a value to a safe string suitable for PDF rendering."""
    if v is None:
        return ''
    return safe_text(v)


def _fmt_date_for_display(d: Any):
    if d is None:
        return None
    s = str(d)
    parts = s.split('-')
    if len(parts) >= 2:
        yyyy = parts[0]
        mm = parts[1]
        try:
            mname = calendar.month_abbr[int(mm)]
            return f"{mname} {yyyy}"
        except Exception:
            return s
    return s


def sanitize_data(data: ResumeSchema) -> ResumeSchema:
    """Return a sanitized ResumeSchema instance without converting to raw dict."""

    header = HeaderSchema(
        name=sanitize_value(data.header.name),
        email=sanitize_value(data.header.email),
        phone=sanitize_value(data.header.phone),
        title=sanitize_value(data.header.title),
    )

    roles: list[RoleSchema] = []

    for r in data.roles:
        start = r.start
        end = r.end
        legacy = getattr(r, 'dates', None)

        # Format display string
        disp = ''
        if start or end:
            s_s = _fmt_date_for_display(start)
            s_e = _fmt_date_for_display(end) if end else None
            if s_s and s_e:
                disp = f"{s_s} - {s_e}"
            elif s_s and s_e is None:
                disp = f"{s_s} - Present"
            elif s_s:
                disp = s_s
        elif legacy:
            disp = sanitize_value(legacy)

        # Employment type
        employment = r.employment if isinstance(r.employment, EmploymentType) else EmploymentType.PERMANENT

        # Preserve None for empty strings
        def _maybe_sanitize_str(v) -> str | None:
            return sanitize_value(v) if v not in (None, '') else None

        role = RoleSchema(
            role=sanitize_value(r.role),
            company=sanitize_value(r.company),
            start=sanitize_value(start),
            end=_maybe_sanitize_str(end),
            location=sanitize_value(r.location),
            employment=employment,
            done=sanitize_value(r.done),
            stack=sanitize_value(r.stack),
        )

        roles.append(role)

    return ResumeSchema(header=header, roles=roles)
