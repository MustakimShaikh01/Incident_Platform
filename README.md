
```markdown
# Incident Management Platform

A distributed incident and change management platform built using **Python, Spring Boot, React, and Docker**.

This project focuses on **real-world backend engineering problems** such as
incident detection, error analysis, trend tracking, and safe automation with
human approval.

The goal is to demonstrate **clean architecture, service boundaries, and production-style workflows**, not toy examples.

---

## 🧱 System Architecture

```

UI (React)
↓
API (Spring Boot)
↓
Engine (Python / Flask)

````

Each service is independently deployable and communicates over HTTP.
All components are containerized and orchestrated using Docker Compose.

---

## 🔧 Tech Stack

- **Frontend:** React
- **Backend API:** Java, Spring Boot
- **Incident Engine:** Python, Flask
- **Infrastructure:** Docker, Docker Compose

---

## 🧠 Key Capabilities

- Asynchronous incident processing (non-blocking APIs)
- Structured error classification
- Confidence scoring for diagnosis reliability
- Error frequency and trend tracking
- Dependency and version conflict detection
- Approval-based decision flow for safe automation
- Clear separation of responsibilities across services

---

## ▶️ Running the Project Locally

### Prerequisites
- Docker
- Docker Compose

### Start all services
```bash
docker compose up --build
````

### Services

* **UI:** [http://localhost:3000](http://localhost:3000)
* **API:** [http://localhost:8080](http://localhost:8080)
* **Engine:** [http://localhost:5001](http://localhost:5001)

---

## 🧪 Example API Calls

### Approve an Incident (API Service)

```bash
curl -X POST http://localhost:8080/incident/approve \
  -H "Content-Type: application/json" \
  -d '{"id":"INC-101"}'
```

### Submit Incident for Analysis (Engine Service)

```bash
curl -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "error_type": "ZeroDivisionError",
    "message": "division by zero",
    "stacktrace": ["File calc.py line 10 return a / b"]
  }'
```

The engine processes incidents asynchronously and logs the analysis result
internally for audit and follow-up actions.

---

## 🛡 Design Principles

* Clear service boundaries
* Defensive automation (no blind fixes)
* Human-in-the-loop approvals
* Stateless APIs with stateful analysis tracking
* Simple, extensible error knowledge base
* Production-oriented defaults

---

## 📂 Project Structure

```
services/
├── api/        # Spring Boot backend
├── engine/     # Python incident analysis engine
└── ui/         # React frontend
```

---

## 🚀 Planned Enhancements

* Email-based approval workflow
* Persistent storage using PostgreSQL
* Authentication and authorization
* Event-driven communication (Kafka / RabbitMQ)
* Metrics, monitoring, and observability

---

```
