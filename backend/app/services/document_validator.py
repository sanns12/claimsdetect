# backend/utils/document_validator.py

import re
from datetime import datetime, date
from typing import List, Dict, Any


# =====================================================
# DATE PARSING ENGINE
# =====================================================

_MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def _normalize_year(y: int) -> int:
    if y < 100:
        return 2000 + y if y <= 68 else 1900 + y
    return y


def _safe_date(y: int, m: int, d: int):
    try:
        return date(y, m, d)
    except ValueError:
        return None


def _parse_numeric_triplet(a: int, b: int, c: int, raw_a: str, raw_b: str, raw_c: str):
    candidates = []

    # yyyy-mm-dd / yyyy-dd-mm
    if len(raw_a) == 4:
        y = _normalize_year(a)
        candidates.extend([(y, b, c), (y, c, b)])

    # dd-mm-yyyy / mm-dd-yyyy
    elif len(raw_c) in (2, 4):
        y = _normalize_year(c)
        if a > 12 and b <= 12:
            candidates.append((y, b, a))  # dd/mm/yyyy
        elif b > 12 and a <= 12:
            candidates.append((y, a, b))  # mm/dd/yyyy
        else:
            # ambiguous: try day-first then month-first
            candidates.extend([(y, b, a), (y, a, b)])

    for y, m, d in candidates:
        parsed = _safe_date(y, m, d)
        if parsed:
            return parsed
    return None


def parse_possible_date(text):
    if not text:
        return None

    value = str(text).strip()
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"(\d{1,2})(st|nd|rd|th)\b", r"\1", value, flags=re.IGNORECASE)
    value = re.sub(r"[,\u00A0]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    # 1) ISO first (including timezone)
    iso_candidate = value.replace("Z", "+00:00").replace("z", "+00:00")
    try:
        return datetime.fromisoformat(iso_candidate).date()
    except (ValueError, TypeError):
        pass

    # Strip trailing time part (e.g., "2026-03-01 14:30:00")
    date_only = re.sub(
        r"[T\s]\d{1,2}:\d{2}(:\d{2}(\.\d+)?)?(\s?(AM|PM|am|pm))?([+-]\d{2}:?\d{2}|Z|z)?$",
        "",
        value,
    ).strip()

    # 2) strptime set for many common patterns
    candidates = {
        value,
        date_only,
        value.replace(".", "/"),
        value.replace(".", "-"),
        value.replace("/", "-"),
        value.replace(",", ""),
    }

    formats = [
        "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
        "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y",
        "%m-%d-%Y", "%m/%d/%Y", "%m.%d.%Y",
        "%d-%m-%y", "%d/%m/%y", "%d.%m.%y",
        "%m-%d-%y", "%m/%d/%y", "%m.%d.%y",
        "%d-%b-%Y", "%d/%b/%Y", "%d %b %Y", "%d %b, %Y",
        "%d-%B-%Y", "%d/%B/%Y", "%d %B %Y", "%d %B, %Y",
        "%b %d %Y", "%b %d, %Y",
        "%B %d %Y", "%B %d, %Y",
        "%d-%b-%y", "%d/%b/%y", "%d %b %y", "%d %b, %y",
        "%d-%B-%y", "%d/%B/%y", "%d %B %y", "%d %B, %y",
        "%b %d %y", "%b %d, %y",
        "%B %d %y", "%B %d, %y",
        "%Y%m%d", "%d%m%Y", "%m%d%Y",
    ]

    for candidate in candidates:
        normalized = candidate.strip()
        for fmt in formats:
            try:
                return datetime.strptime(normalized, fmt).date()
            except (ValueError, TypeError):
                continue

    # 3) Month word parsing (manual)
    m1 = re.match(r"^(\d{1,2})[\s./-]+([A-Za-z]{3,9})[\s./-]+(\d{2,4})$", date_only)
    if m1:
        d, mon, y = m1.groups()
        mon_num = _MONTHS.get(mon.lower())
        if mon_num:
            return _safe_date(_normalize_year(int(y)), mon_num, int(d))

    m2 = re.match(r"^([A-Za-z]{3,9})[\s./-]+(\d{1,2})[\s./-]+(\d{2,4})$", date_only)
    if m2:
        mon, d, y = m2.groups()
        mon_num = _MONTHS.get(mon.lower())
        if mon_num:
            return _safe_date(_normalize_year(int(y)), mon_num, int(d))

    # 4) Numeric triplet parsing
    parts = re.split(r"[-./\s]+", date_only)
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        a, b, c = map(int, parts)
        parsed = _parse_numeric_triplet(a, b, c, parts[0], parts[1], parts[2])
        if parsed:
            return parsed

    # 5) Compact 8-digit fallback (yyyymmdd / ddmmyyyy / mmddyyyy)
    compact = re.sub(r"\D", "", date_only)
    if len(compact) == 8:
        if compact[:4].isdigit() and compact[:2] in {"19", "20"}:
            parsed = _safe_date(int(compact[:4]), int(compact[4:6]), int(compact[6:8]))
            if parsed:
                return parsed

        a = _safe_date(int(compact[4:8]), int(compact[2:4]), int(compact[0:2]))  # ddmmyyyy
        if a:
            return a

        b = _safe_date(int(compact[4:8]), int(compact[0:2]), int(compact[2:4]))  # mmddyyyy
        if b:
            return b

    return None


# =====================================================
# DATE EXTRACTION FROM DOCUMENT TEXT
# =====================================================

def extract_dates_from_text(text: str):
    if not text:
        return []

    patterns = [
        # ISO date or datetime
        r"\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}(?:[T\s]\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?\b",
        # Numeric d/m/y or m/d/y
        r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b",
        # Day Month Year (with optional ordinal/comma)
        r"\b\d{1,2}(?:st|nd|rd|th)?[-/.\s]+[A-Za-z]{3,9}[-/.\s,]+\d{2,4}\b",
        # Month Day Year
        r"\b[A-Za-z]{3,9}[-/.\s]+\d{1,2}(?:st|nd|rd|th)?[, ]*[-/.\s]*\d{2,4}\b",
        # Compact 8-digit dates
        r"\b\d{8}\b",
    ]

    found_dates = []
    seen = set()

    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            parsed = parse_possible_date(match)
            if parsed and parsed not in seen:
                seen.add(parsed)
                found_dates.append(parsed)

    return found_dates


# =====================================================
# MAIN VALIDATION FUNCTION
# =====================================================

def validate_claim_against_document(
    form_data: Dict[str, Any],
    extracted_text: str
) -> List[str]:

    mismatches = []

    if not extracted_text:
        return ["Document text could not be extracted"]

    # -------------------------------------------------
    # 1️⃣ CLAIM AMOUNT VALIDATION
    # -------------------------------------------------

    numbers = re.findall(r"\d+\.?\d*", extracted_text.replace(",", ""))
    numbers = [float(n) for n in numbers]

    try:
        form_amount = float(form_data.get("claim_amount", 0))
    except (TypeError, ValueError):
        mismatches.append("Invalid claim amount format")
        form_amount = 0

    if form_amount > 0:
        if not any(abs(n - form_amount) < 1 for n in numbers):
            mismatches.append("Claim amount mismatch")

    # -------------------------------------------------
    # 2️⃣ DATE VALIDATION
    # -------------------------------------------------

    extracted_dates = set(extract_dates_from_text(extracted_text))

    admission_date = parse_possible_date(form_data.get("admission_date"))
    discharge_date = parse_possible_date(form_data.get("discharge_date"))

    if not admission_date:
        mismatches.append("Invalid admission date format in form")
    elif admission_date not in extracted_dates:
        mismatches.append("Admission date mismatch")

    if not discharge_date:
        mismatches.append("Invalid discharge date format in form")
    elif discharge_date not in extracted_dates:
        mismatches.append("Discharge date mismatch")

    return mismatches
