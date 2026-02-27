import re
from datetime import datetime


def parse_possible_date(text):
    if not text:
        return None

    value = str(text).strip()
    value = re.sub(r"(\d{1,2})(st|nd|rd|th)", r"\1", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value)

    iso_candidate = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(iso_candidate).date()
    except (ValueError, TypeError):
        pass

    candidates = {
        value,
        value.replace(".", "/"),
        value.replace(".", "-"),
        value.replace("/", "-"),
        value.replace(",", "")
    }

    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%m/%d/%Y",
        "%d-%b-%Y",
        "%d/%b/%Y",
        "%d-%B-%Y",
        "%d/%B/%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d %Y",
        "%B %d %Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%d %b, %Y",
        "%d %B, %Y",
        "%d-%m-%y",
        "%d/%m/%y",
        "%m-%d-%y",
        "%m/%d/%y"
    ]

    for candidate in candidates:
        normalized = candidate.strip()
        for fmt in formats:
            try:
                return datetime.strptime(normalized, fmt).date()
            except (ValueError, TypeError):
                continue

    return None


def extract_dates_from_text(text):
    patterns = [
        r"\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b",
        r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b",
        r"\b\d{1,2}\s+[A-Za-z]{3,9}\s*,?\s*\d{2,4}\b",
        r"\b[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{2,4}\b"
    ]

    found_dates = []

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            parsed = parse_possible_date(match)
            if parsed:
                found_dates.append(parsed)

    return found_dates


def validate_claim_against_document(form_data, extracted_text):
    mismatches = []

    # ---------------- Amount Validation ----------------
    numbers = re.findall(r"\d+\.?\d*", extracted_text.replace(",", ""))
    numbers = [float(n) for n in numbers]

    form_amount = float(form_data["claim_amount"])

    if not any(abs(n - form_amount) < 1 for n in numbers):
        mismatches.append("Claim amount mismatch")

    # ---------------- Date Validation ----------------
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

