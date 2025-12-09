"""Sanitization helpers for resume data and PDF-safe text."""
import calendar


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


def sanitize_data(data):
    """Return a sanitized mapping with 'header' and 'roles' suitable for building PDFs.

    This mirrors the previous logic from `main.py`.
    """
    sanitized = {}
    sanitized['header'] = {}
    for k, v in (data.get('header', {}) or {}).items():
        sanitized['header'][k] = sanitize_value(v)

    sanitized['roles'] = []
    for r in (data.get('roles', []) or []):
        # Prefer explicit start/end fields; fall back to legacy free-text 'dates'
        start = r.get('start')
        end = r.get('end')
        legacy = r.get('dates')

        disp = ''
        if start or end:
            # Normalize start/end to human readable form. Use YYYY-MM or YYYY where available.
            def fmt(d):
                if d is None:
                    return None
                s = str(d)
                # If already in YYYY-MM or YYYY-MM-DD, try to format month name
                parts = s.split('-')
                if len(parts) >= 2:
                    yyyy = parts[0]
                    mm = parts[1]
                    try:
                        mname = calendar.month_abbr[int(mm)]
                        return f"{mname} {yyyy}"
                    except Exception:
                        return s
                # fallback: return raw
                return s

            s_s = fmt(start)
            s_e = fmt(end) if end is not None else None
            if s_s and s_e:
                disp = f"{s_s} - {s_e}"
            elif s_s and (s_e is None):
                disp = f"{s_s} - Present"
            elif s_s:
                disp = s_s
            else:
                disp = ''
        elif legacy:
            disp = sanitize_value(legacy)

        sanitized['roles'].append({
            'role': sanitize_value(r.get('role')),
            'company': sanitize_value(r.get('company')),
            'start': sanitize_value(start),
            'end': sanitize_value(end),
            'dates': sanitize_value(disp),
            'location': sanitize_value(r.get('location')),
            'done': sanitize_value(r.get('done')),
            'stack': sanitize_value(r.get('stack')),
        })
    return sanitized
