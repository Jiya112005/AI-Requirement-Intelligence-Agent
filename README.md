# AI Requirement Intelligence System

A backend-driven system that transforms **vague, unstructured business inputs** into **structured requirements, clarity insights, and feasibility analysis** using a multi-agent LLM pipeline.

---

## 🎯 Problem

In real-world projects (especially ERP and SaaS), client requirements are often:

- vague  
- incomplete  
- inconsistent  

This leads to:
- multiple clarification cycles  
- incorrect scope estimation  
- costly rework during development  

---

## 💡 Solution

This system acts as a **pre-PRD intelligence layer**:
    Raw input
       |
    Extraction -> Clarification -> Feasibility 
       |
    Structured Requirements + Insights
    
---

## ⚙️ Current Capabilities (Phase 1–3)

---

### 🟢 Phase 1 & 2: Foundation (Completed)

- **Input Ingestion**
  - `/api/upload` supports:
    - raw JSON text  
    - PDF files (via PyMuPDF)

- **Preprocessing**
  - `clean_text()` removes noise and normalizes input  

- **Authentication & Storage**
  - JWT-based user authentication  
  - SQLite database:
    - Users  
    - Documents  
    - Requirements  

---

### 🟡 Phase 3: Local Intelligence Engine (Completed)

A synchronous multi-agent pipeline orchestrated via `LLMService`.

---

#### 🔹 Agent 1 — Extractor
- Identifies:
  - core features  
  - priorities  
- Converts messy input → structured requirement data  

---

#### 🔹 Agent 2 — Clarifier
- Detects:
  - vague / ambiguous terms  
- Generates:
  - clarity score  
  - clarification questions  

---

#### 🔹 Agent 3 — Feasibility Analyzer
- Evaluates:
  - technical constraints  
  - dependencies  
  - risks  

---

#### 🔹 Data Retrieval APIs
- `/api/history` → fetch processed documents  
- `/api/document/<id>` → fetch full analysis  

---

## 🧠 Example Output

**Input:**  
 "We want a system to manage everything and be scalable"

  **Output:**
  ```json
  {
    "features": ["System Management"],
    "clarity_score": 0.4,
    "missing_info": ["What modules?", "Expected scale?"],
    "questions": ["What specific features are required?"],
    "feasibility": "Medium",
    "risks": ["Undefined scope may cause delays"]
  } 
```

**Architecture:**

Client Input

   ↓
   
Flask API (/upload)

   ↓
   
Preprocessing Layer

   ↓
   
LLMService (Orchestrator)
   
   ├── Extractor Agent
   
   ├── Clarifier Agent
   
   └── Feasibility Agent
   
   ↓

SQLite Database

   ↓

API Retrieval Endpoints

**Notes on the idea**

->This project focuses on the earliest and most overlooked stage of software development: requirement understanding.

->Instead of generating final documents directly, the system emphasizes:
           identifying ambiguity 
           asking the right questions
           evaluating feasibility before execution

-> The goal is to reduce dependency on manual interpretation and improve alignment between business needs and technical execution.

-> Designed as an API-first system, making it adaptable for integration into existing workflows or tools.

