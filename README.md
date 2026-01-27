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

