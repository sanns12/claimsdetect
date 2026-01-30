# 📘 BACKEND DOCUMENTATION

**Role:** Teammate 3 – Backend & System Flow
**Project:** Insurance Claim Management Platform
**Stack:** Python · FastAPI · SQLAlchemy · JWT

---

## 1. 📁 Backend Folder Structure

```
backend/
├── __init__.py
├── main.py
├── database.py
├── models.py
├── auth.py
├── claim_routes.py
├── dashboard_routes.py
├── seed_data.py
├── ml_model.py
├── risk_engine.py
├── lime_explainer.py
├── file_verification.py
├── company_trust_logic.py
```

---

## 2. 📄 FILE-WISE BREAKDOWN (WHAT EACH FILE DOES)

---

### 🔹 `backend/main.py`

**Purpose:** Application entry point

**Contains:**

* FastAPI app initialization
* Database table creation
* Router registration:

  * Authentication
  * Claims
  * Dashboard

**Why it exists:**
Acts as the **spine** of the backend. All APIs are wired here.

---

### 🔹 `backend/database.py`

**Purpose:** Database configuration

**Contains:**

* SQLite database connection
* SQLAlchemy engine
* SessionLocal
* `get_db()` dependency

**Why it exists:**
Single source of truth for database access.

---

### 🔹 `backend/models.py`

**Purpose:** Database schema (ORM models)

**Contains:**

* `User` model (id, name, email, role, password)
* `Claim` model (claim_id, user_id, company_id, status, documents, risk_score)
* `Company` model (company_id, trust_score, flagged_count)
* `ClaimStatus` enum with exact values:

  * Submitted
  * AI Processing
  * Manual Review
  * Approved
  * Flagged
  * Fraud

**Why it exists:**
Defines the **data contract** used by backend, frontend, and ML.

---

### 🔹 `backend/auth.py`

**Purpose:** Authentication & Authorization

**Contains:**

* JWT token generation
* Password hashing (Argon2)
* `/login` API
* `get_current_user()` dependency
* `require_role()` role-based access control
* HTTPBearer security for Swagger & APIs

**Roles supported:**

* user
* hospital
* insurance

**Why it exists:**
Controls **who can access what** across the system.

---

### 🔹 `backend/claim_routes.py`

**Purpose:** Core claim lifecycle APIs

**Endpoints implemented:**

1. `POST /claims/submit` – User submits a claim
2. `GET /claims/view` – Role-based claim viewing
3. `PUT /claims/{id}/status` – Hospital/Insurance updates claim status
4. `POST /claims/{id}/upload-documents` – Upload additional documents

**Special logic:**

* ML hooks triggered when status → **AI Processing**
* Single DB commit per request
* Strict role enforcement

**Why it exists:**
This is the **core business logic** of the platform.

---

### 🔹 `backend/dashboard_routes.py`

**Purpose:** Analytics & admin dashboard APIs

**Endpoints implemented:**

* `GET /dashboard/summary`

  * total claims
  * approved
  * flagged
  * fraud
* `GET /dashboard/company-trust`

  * company trust scores

**Access:** Insurance role only

**Why it exists:**
Supports **admin / insurer dashboards**.

---

### 🔹 `backend/seed_data.py`

**Purpose:** Utility script to seed dummy users

**Creates test users:**

* [user@test.com](mailto:user@test.com)
* [hospital@test.com](mailto:hospital@test.com)
* [insurance@test.com](mailto:insurance@test.com)

**Why it exists:**
Enables immediate Swagger testing and demo without signup flow.

---

### 🔹 `backend/ml_model.py`

**Purpose:** ML prediction stub (no logic)

**Contains:**

* `predict_fraud(claim_data)`

**Why it exists:**
Defines a **clear interface** for ML teammate to plug models later.

---

### 🔹 `backend/risk_engine.py`

**Purpose:** Risk score calculation stub

**Contains:**

* `calculate_risk(claim_data, ml_result)`

**Why it exists:**
Separates raw ML output from business risk scoring.

---

### 🔹 `backend/lime_explainer.py`

**Purpose:** Explainability stub

**Contains:**

* `explain_decision(claim_data, ml_result)`

**Why it exists:**
Supports future explainable AI (LIME/SHAP) integration.

---

### 🔹 `backend/file_verification.py`

**Purpose:** Placeholder for document verification logic

**Current state:** Empty / stub

**Why it exists:**
Reserved for future document validation (PDF checks, OCR, etc.).

---

### 🔹 `backend/company_trust_logic.py`

**Purpose:** Placeholder for company trust score logic

**Current state:** Empty / stub

**Why it exists:**
Future logic to dynamically update insurer trust scores.

---

## 3. 🔐 SECURITY & ACCESS SUMMARY

* JWT-based authentication
* HTTPBearer used for Swagger & APIs
* Role-based access enforced at route level
* Unauthorized access returns 401 / 403

---

## 4. 🧠 ML INTEGRATION STATUS

* No ML logic implemented (by design)
* Clean hooks available
* Backend is ML-ready without refactor

---

## 5. ✅ CURRENT BACKEND STATUS

* Core backend **complete**
* APIs stable and testable
* Ready for:

  * Frontend integration
  * ML integration
  * Hackathon demo

---

## 6. 🧑‍💻 RESPONSIBILITY NOTE

All files and logic listed above were implemented and owned by
**Teammate 3 (Backend & System Flow)**.

