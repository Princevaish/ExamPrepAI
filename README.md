# 🚀 ExamPrepAI — AI-Powered Exam Preparation SaaS

ExamPrepAI is a **production-grade AI SaaS platform** that generates **exam-ready MCQs, quizzes, summaries, and tutorials** using Large Language Models — built with **real backend architecture**, not demo shortcuts.

This project demonstrates **backend maturity, async systems, AI orchestration, Dockerized deployment, and SaaS-ready design**.

---

## 🧠 Why ExamPrepAI Exists

Most AI projects stop at:
- synchronous requests
- temporary storage
- fragile OAuth
- demo-level design

**ExamPrepAI goes further**:
- Handles long-running AI tasks asynchronously
- Uses PostgreSQL safely (OAuth edge cases handled)
- Generates PDFs without server disk abuse
- Fully Dockerized multi-service architecture
- Ready for monetization, scaling, and production

---

## ✨ Core Features

### 🤖 AI Capabilities
- MCQ generation (difficulty-based)
- Quiz generation
- Short & detailed summaries
- Tutorial-style explanations
- Structured revision notes

### 📄 PDF Generation (SaaS-Safe)
- PDFs generated **entirely in memory**
- No files stored on server disk
- Downloads go directly to the **user’s device**
- Prevents disk-space abuse & legal issues

### ⚙️ Asynchronous Processing
- Celery handles all AI workloads
- Redis as message broker
- PostgreSQL-backed result storage
- Auto-expiry of task results

### 🔐 Authentication
- Email + Google OAuth (django-allauth)
- PostgreSQL-safe OAuth handling
- Auto-generated usernames for social login users
- Session edge cases handled correctly

---

## 🏗 Architecture Overview

Client (Browser)
↓
Django Web App
↓ (async task)
Redis (Broker)
↓
Celery Worker
↓
LLM APIs (Groq / LLaMA)
↓
PostgreSQL (Results + Metadata)

yaml
Copy code

This mirrors **real-world SaaS backend architecture**.

---

## 🛠 Tech Stack

| Layer | Technology |
|-----|-----------|
| Backend | Django 5 |
| Async Tasks | Celery |
| Broker | Redis |
| Database | PostgreSQL |
| AI | LangChain + Groq (LLaMA) |
| Auth | django-allauth (Google OAuth) |
| PDFs | FPDF (in-memory) |
| DevOps | Docker, Docker Compose |

---

## 📁 Project Structure

ExamPrepAI/
├── ai_core/ # AI logic, Celery tasks, signals
├── home/ # Core Django app
├── templates/ # UI templates
├── static/ # Static assets
├── hello/ # Django project config
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py

yaml
Copy code

---

## ⚡ Local Setup (Docker)

### 1️⃣ Clone
```bash
git clone https://github.com/Princevaish/ExamPrepAI.git
cd ExamPrepAI
2️⃣ Create .env
env
Copy code
DEBUG=1
SECRET_KEY=your-secret-key

POSTGRES_DB=examprep_dost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_HOST=db

REDIS_URL=redis://redis:6379/0

GROQ_API_KEY=your_groq_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
3️⃣ Run
bash
Copy code
docker-compose up --build
App runs at:
👉 http://localhost:8000

🔐 Admin Access
bash
Copy code
docker-compose exec web python manage.py createsuperuser
Admin panel:
👉 http://localhost:8000/admin

🧪 Production Safety Measures
python
Copy code
CELERY_RESULT_EXPIRES = 3600  # Auto-cleanup after 1 hour
Prevents PostgreSQL bloat

No cron jobs required

Safe for long-term SaaS use

🚀 Designed for Growth
This architecture already supports:

💳 Payment integration (Razorpay / Stripe)

🎯 Tier-based usage limits

⚡ Redis caching for repeated prompts

📊 Analytics & usage tracking

☁️ Cloud deployment (AWS / Railway / Render)

No refactor required.

🧠 What This Project Demonstrates
✔ Backend system design
✔ Async task orchestration
✔ OAuth edge-case handling
✔ PostgreSQL vs SQLite differences
✔ Docker-first mindset
✔ AI integration at scale
✔ SaaS-ready thinking

This is not a CRUD app and not a tutorial clone.

👨‍💻 Author
Prince Vaish
Final-year Computer Science student
Backend • AI • System Design
