import re

def normalize_date(date_str):
    return date_str.replace("-", "").replace("/", "")

def validate_claim_against_document(form_data, extracted_text):
    mismatches = []
    text = extracted_text.lower()

    # Patient name (loose match)
    if form_data["patient_name"].lower() not in text:
        mismatches.append("Patient name mismatch")

    # Amount tolerance
    numbers = re.findall(r"\d+\.?\d*", extracted_text)
    numbers = [float(n) for n in numbers]
    form_amount = float(form_data["claim_amount"])

    if not any(abs(n - form_amount) < 1 for n in numbers):
        mismatches.append("Claim amount mismatch")

    # Admission date (normalized)
    admission = normalize_date(form_data["admission_date"])
    if admission not in normalize_date(extracted_text):
        mismatches.append("Admission date mismatch")

    # Discharge date (normalized)
    discharge = normalize_date(form_data["discharge_date"])
    if discharge not in normalize_date(extracted_text):
        mismatches.append("Discharge date mismatch")

    return mismatches