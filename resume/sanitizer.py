"""Sanitization helpers for resume data and PDF-safe text.

This module converts raw mappings into typed DTOs (Pydantic models) while
sanitizing strings for PDF rendering.
"""
import calendar
from resume.repository import HeaderSchema, RoleSchema, ResumeSchema, EmploymentType


def safe_text(text):
    # robust low-level replacer; accept non-str and None
    if text is None:
        return ''
    s = str(text)
    return s.replace("\u2013", "-").replace("\u2014", "-").replace("\u2019", "'")


def sanitize_value(v):
    """Convert a value to a safe string suitable for PDF rendering."""
    if v is None:
        return ''
    return safe_text(v)


def _fmt_date_for_display(d):
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


def sanitize_data(raw):
    """Return a `ResumeSchema` instance built from raw mapping `raw`.

    This preserves the previous sanitization but returns typed models used by
    the rest of the codebase.
    """
    # Accept either a raw mapping or a Pydantic ResumeSchema instance.
    if hasattr(raw, 'dict'):
        raw = raw.dict()

    header_raw = (raw.get('header', {}) or {})
    header = HeaderSchema(
        name=sanitize_value(header_raw.get('name')),
        email=sanitize_value(header_raw.get('email')),
        phone=sanitize_value(header_raw.get('phone')),
        title=sanitize_value(header_raw.get('title')),
    )

    roles = []
    for r in (raw.get('roles', []) or []):
        start = r.get('start')
        end = r.get('end')
        legacy = r.get('dates')

        disp = ''
        if start or end:
            s_s = _fmt_date_for_display(start)
            s_e = _fmt_date_for_display(end) if end is not None else None
            if s_s and s_e:
                disp = f"{s_s} - {s_e}"
            elif s_s and (s_e is None):
                disp = f"{s_s} - Present"
            elif s_s:
                disp = s_s
        elif legacy:
            disp = sanitize_value(legacy)

        employment_val = r.get('employment')
        if isinstance(employment_val, EmploymentType):
            employment = employment_val
        else:
            try:
                employment = EmploymentType(employment_val)
            except Exception:
                employment = EmploymentType.PERMANENT

        # Preserve None for start/end if they are empty so validation rules
        # on RoleSchema (pattern for YYYY-MM) are respected. Only sanitize
        # non-empty string fields.
        def _maybe_sanitize_str(v):
            return sanitize_value(v) if (v is not None and v != '') else None

        role = RoleSchema(
            role=sanitize_value(r.get('role')),
            company=sanitize_value(r.get('company')),
            start=_maybe_sanitize_str(start),
            end=_maybe_sanitize_str(end),
            location=sanitize_value(r.get('location')),
            employment=employment,
            done=sanitize_value(r.get('done')),
            stack=sanitize_value(r.get('stack')),
        )
        # Keep a formatted dates string on the instance for PDF rendering
        setattr(role, 'dates', sanitize_value(disp))
        # Preserve optional is_hybrid flag if present
        if 'is_hybrid' in r:
            setattr(role, 'is_hybrid', bool(r.get('is_hybrid')))
        roles.append(role)

    return ResumeSchema(header=header, roles=roles)
